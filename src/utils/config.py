"""
Configuration management utilities for Lightime Pomodoro Timer
"""

import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from ..models.config import LightimeConfig, ConfigPaths
except ImportError:
    # Fallback for direct execution
    from models.config import LightimeConfig, ConfigPaths


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration file changes"""

    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        super().__init__()

    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            # Check if this is a config file we're watching
            if file_path.name in ['config.yaml', 'local.yaml'] and file_path.parent == self.config_manager.config_paths.config_dir:
                self.config_manager._reload_config()


class ConfigManager:
    """Configuration manager with hot-reloading capabilities"""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_paths = ConfigPaths(config_dir)
        self._config: Optional[LightimeConfig] = None
        self._observers: list[Observer] = []
        self._change_callbacks: list[callable] = []
        self._config_lock = False  # Prevent reload loops

        # Ensure config directory exists
        self.config_paths.config_dir.mkdir(parents=True, exist_ok=True)

        # Load initial configuration
        self._load_config()

        # Setup file watching for hot reload
        self._setup_file_watching()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()

    @property
    def config(self) -> LightimeConfig:
        """Get current configuration (loads if not already loaded)"""
        if self._config is None:
            self._load_config()
        return self._config

    def add_change_callback(self, callback: callable) -> None:
        """Add a callback to be called when configuration changes"""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: callable) -> None:
        """Remove a configuration change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def _notify_change_callbacks(self) -> None:
        """Notify all registered callbacks about configuration changes"""
        for callback in self._change_callbacks:
            try:
                callback(self.config)
            except Exception as e:
                print(f"Error in config change callback: {e}")

    def _load_config(self) -> None:
        """Load configuration from files"""
        try:
            # Start with default configuration
            merged_config: Dict[str, Any] = {}

            # Load default config if it exists
            default_config_file = self._get_default_config_file()
            if default_config_file.exists():
                with open(default_config_file, 'r', encoding='utf-8') as f:
                    default_data = yaml.safe_load(f) or {}
                    merged_config.update(default_data)

            # Load and merge user config if it exists
            if self.config_paths.user_config_file.exists():
                with open(self.config_paths.user_config_file, 'r', encoding='utf-8') as f:
                    user_data = yaml.safe_load(f) or {}
                    # Deep merge user config with default
                    merged_config = self._deep_merge(merged_config, user_data)

            # Load and merge local config if it exists
            if self.config_paths.local_config_file.exists():
                with open(self.config_paths.local_config_file, 'r', encoding='utf-8') as f:
                    local_data = yaml.safe_load(f) or {}
                    # Deep merge local config
                    merged_config = self._deep_merge(merged_config, local_data)

            # Create configuration object
            self._config = LightimeConfig.from_dict(merged_config)

        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Fallback to default configuration
            self._config = LightimeConfig()

    def _reload_config(self) -> None:
        """Reload configuration (for hot reload)"""
        if self._config_lock:
            return  # Prevent reload loops

        self._config_lock = True
        try:
            old_config = self._config
            self._load_config()

            # Notify callbacks if configuration actually changed
            if old_config != self._config:
                self._notify_change_callbacks()

        except Exception as e:
            print(f"Error reloading configuration: {e}")
        finally:
            self._config_lock = False

    def _get_default_config_file(self) -> Path:
        """Get the default configuration file path"""
        # Try to find default.yaml in the package directory first
        try:
            # Get the directory where this module is located
            module_dir = Path(__file__).parent.parent.parent
            package_config = module_dir / "config" / "default.yaml"
            if package_config.exists():
                return package_config
        except Exception:
            pass

        # Fallback to user config directory
        return self.config_paths.default_config_file

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _setup_file_watching(self) -> None:
        """Setup file system watching for configuration changes"""
        try:
            if not self.config_paths.config_dir.exists():
                return

            # Create observer
            observer = Observer()
            event_handler = ConfigFileHandler(self)

            # Watch the config directory
            observer.schedule(event_handler, str(self.config_paths.config_dir), recursive=False)
            observer.start()

            self._observers.append(observer)

        except Exception as e:
            print(f"Error setting up file watching: {e}")

    def create_user_config(self, config: Optional[LightimeConfig] = None) -> None:
        """Create user configuration file"""
        try:
            config_to_save = config or self.config
            config_data = config_to_save.to_dict()

            with open(self.config_paths.user_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)

        except Exception as e:
            print(f"Error creating user config: {e}")

    def backup_config(self) -> bool:
        """Create a backup of current user configuration"""
        try:
            if not self.config_paths.user_config_file.exists():
                return False

            backup_file = self.config_paths.user_config_file.with_suffix('.yaml.backup')
            import shutil
            shutil.copy2(self.config_paths.user_config_file, backup_file)
            return True

        except Exception as e:
            print(f"Error backing up configuration: {e}")
            return False

    def restore_config_backup(self) -> bool:
        """Restore configuration from backup"""
        try:
            backup_file = self.config_paths.user_config_file.with_suffix('.yaml.backup')
            if not backup_file.exists():
                return False

            import shutil
            shutil.copy2(backup_file, self.config_paths.user_config_file)

            # Reload the restored configuration
            self._reload_config()
            return True

        except Exception as e:
            print(f"Error restoring configuration backup: {e}")
            return False

    def validate_config_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate a configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return False, "Configuration must be a dictionary"

            # Try to create config object to validate
            config = LightimeConfig.from_dict(data)
            return True, None

        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, f"Configuration error: {e}"

    def get_config_files_info(self) -> Dict[str, Any]:
        """Get information about configuration files"""
        info = {
            'config_directory': str(self.config_paths.config_dir),
            'files': {}
        }

        for file_name in ['default.yaml', 'config.yaml', 'local.yaml']:
            file_path = self.config_paths.config_dir / file_name
            info['files'][file_name] = {
                'path': str(file_path),
                'exists': file_path.exists(),
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'modified': file_path.stat().st_mtime if file_path.exists() else None
            }

        return info

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        try:
            # Remove user and local config files
            if self.config_paths.user_config_file.exists():
                self.config_paths.user_config_file.unlink()

            if self.config_paths.local_config_file.exists():
                self.config_paths.local_config_file.unlink()

            # Reload configuration
            self._load_config()
            self._notify_change_callbacks()

        except Exception as e:
            print(f"Error resetting configuration: {e}")

    def update_config(self, updates: Dict[str, Any], create_user_file: bool = True) -> bool:
        """Update specific configuration values"""
        try:
            current_config_data = self.config.to_dict()
            updated_config_data = self._deep_merge(current_config_data, updates)

            # Validate updated configuration
            updated_config = LightimeConfig.from_dict(updated_config_data)

            # Save to user config file if requested
            if create_user_file:
                with open(self.config_paths.user_config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(updated_config_data, f, default_flow_style=False, indent=2)

            # Update current configuration
            self._config = updated_config
            self._notify_change_callbacks()

            return True

        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False

    def shutdown(self) -> None:
        """Clean shutdown of configuration manager"""
        # Stop file watchers
        for observer in self._observers:
            try:
                observer.stop()
                observer.join(timeout=1.0)
            except Exception as e:
                print(f"Error stopping file observer: {e}")

        self._observers.clear()
        self._change_callbacks.clear()