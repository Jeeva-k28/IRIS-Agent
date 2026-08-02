import os
import runpy

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(script_dir, "Iris", "iris.py")
    runpy.run_path(target_script, run_name="__main__")
