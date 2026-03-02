try:
    from ai_module import detect_objects
    print("AI Module Imported Successfully")
except ImportError as e:
    print(f"Import Failed: {e}")
except Exception as e:
    print(f"Error: {e}")
