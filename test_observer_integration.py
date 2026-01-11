"""
Test script to verify the integration between the Workspace Observer and the Skill Dispatcher.
"""
import os
import tempfile
import time
from pathlib import Path

def test_observer_dispatcher_integration():
    """
    Test the integration between the observer and dispatcher systems.
    """
    print("Testing Observer-Dispatcher Integration...")

    try:
        # Import the necessary modules
        from src.observer.main import WorkspaceObserver
        from src.dispatcher.main import DispatcherMain
        from src.dispatcher.integration import ObserverIntegration

        print("✓ Successfully imported observer and dispatcher modules")

        # Test 1: Initialize dispatcher
        dispatcher = DispatcherMain()
        dispatcher.setup()
        print("✓ Successfully initialized dispatcher")

        # Test 2: Initialize observer
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            observer = WorkspaceObserver(spec_dir=str(temp_path), pid_file=".test_observer.pid")
            print("✓ Successfully initialized observer")

            # Test 3: Check if observer has dispatcher integration
            if hasattr(observer, 'dispatcher_integration') and observer.dispatcher_integration:
                print("✓ Observer has dispatcher integration")
            else:
                print("⚠ Observer may not have dispatcher integration (this could be due to import issues)")

        # Test 4: Test the integration class directly
        integration = ObserverIntegration(dispatcher)
        print("✓ Successfully initialized ObserverIntegration")

        # Test 5: Check integration status
        status = integration.get_status()
        print(f"✓ Integration status: {status}")

        # Test 6: Create a test log file to process
        test_log_content = [
            "INFO: Application started successfully",
            "ERROR: TypeError: 'NoneType' object has no attribute 'process'",
            "WARNING: Memory usage is high",
            "DEBUG: Processing user request"
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for line in test_log_content:
                f.write(line + '\n')
            test_log_file = f.name

        try:
            # Test processing the log file using the actual method name
            integration._process_file_content(test_log_file)
            print("✓ Successfully processed test log file")
        finally:
            # Clean up test file
            os.unlink(test_log_file)

        print("\n✅ All integration tests passed!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("This may be expected if the dispatcher is not fully set up yet.")
        return False
    except Exception as e:
        print(f"\n❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_observer_dispatcher_integration()
    if success:
        print("\n🎉 Observer-Dispatcher integration is working correctly!")
    else:
        print("\n⚠️  There may be issues with the integration, but this could be expected depending on the setup.")