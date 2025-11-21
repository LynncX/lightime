#!/usr/bin/env python3

"""
Main entry point for Lightime Pomodoro Timer
"""

import sys
import argparse
import logging
import signal
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app_context import ApplicationContext, initialize_app, shutdown_app
    from utils.error_handling import ErrorSeverity
except ImportError as e:
    # Try relative imports as fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.app_context import ApplicationContext, initialize_app, shutdown_app
    from src.utils.error_handling import ErrorSeverity


def setup_logging(debug: bool = False) -> None:
    """Setup basic logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        prog="lightime",
        description="Lightweight Pomodoro timer for Linux desktops"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration directory"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run integration tests and exit"
    )

    parser.add_argument(
        "--diagnostics",
        type=str,
        metavar="FILE",
        help="Export diagnostic information to FILE"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()
    setup_logging(args.debug)

    logger = logging.getLogger(__name__)
    logger.info("Starting Lightime Pomodoro Timer v1.0.0")

    try:
        # Initialize application context
        app_context = initialize_app(
            config_dir=Path(args.config) if args.config else None
        )

        # Handle special modes
        if args.test:
            return run_tests(app_context)
        elif args.diagnostics:
            return export_diagnostics(app_context, args.diagnostics)

        # Start the application
        if not app_context.start():
            logger.error("Failed to start application")
            return 1

        # Setup graceful shutdown handler
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            shutdown_app()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Main application loop
        try:
            logger.info("Lightime application running...")

            # Start GUI interface
            from gui.application import GUIManager
            gui_manager = GUIManager(app_context)

            if not gui_manager.initialize():
                logger.error("Failed to initialize GUI")
                return 1

            # Run GUI application (blocks until quit)
            return_code = gui_manager.run()
            return return_code

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")

        # Stop the application
        app_context.stop()
        return 0

    except Exception as e:
        logger.error(f"Failed to start Lightime: {e}")
        return 1
    finally:
        # Ensure cleanup
        shutdown_app()


def run_tests(app_context: ApplicationContext) -> int:
    """Run integration tests"""
    logger = logging.getLogger(__name__)

    logger.info("Running integration tests...")

    test_results = app_context.test_integration()

    print("\nIntegration Test Results:")
    print("=" * 40)

    all_passed = True
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            print(f"{test_name}:")
            for subtest, subresult in result.items():
                status = "PASS" if subresult else "FAIL"
                print(f"  {subtest}: {status}")
                if not subresult:
                    all_passed = False
        else:
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False

    print("=" * 40)
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")

    return 0 if all_passed else 1


def export_diagnostics(app_context: ApplicationContext, file_path: str) -> int:
    """Export diagnostic information"""
    logger = logging.getLogger(__name__)

    logger.info(f"Exporting diagnostics to {file_path}")

    success = app_context.export_diagnostics(file_path)

    if success:
        print(f"Diagnostics exported successfully to {file_path}")
        return 0
    else:
        print(f"Failed to export diagnostics to {file_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
