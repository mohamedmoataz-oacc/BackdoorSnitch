import onnx
import json

def scan_model(model_path, output_path, verbose=False):
    try:
        model = onnx.load(model_path)

        # Placeholder scan logic
        result = {
            "model_path": model_path,
            "status": "clean",  # Replace with actual analysis
            "details": "No known triggers found.",
        }

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=4)

        if verbose:
            print(json.dumps(result, indent=4))

        print(f"[+] Scan complete. Output saved to {output_path}")

    except Exception as e:
        error_output = {
            "model_path": model_path,
            "status": "error",
            "error": str(e)
        }
        with open(output_path, 'w') as f:
            json.dump(error_output, f, indent=4)
        if verbose:
            print(json.dumps(error_output, indent=4))
        print(f"[!] Scan failed. See {output_path}")
