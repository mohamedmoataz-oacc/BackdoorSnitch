import onnx
import json

def view_model(model_path, verbose=False):
    try:
        model = onnx.load(model_path)
        info = {
            "model_path": model_path,
            "inputs": [i.name for i in model.graph.input],
            "outputs": [o.name for o in model.graph.output],
            "node_types": [n.op_type for n in model.graph.node],
            "node_count": len(model.graph.node)
        }

        print(json.dumps(info, indent=4))
        if verbose:
            print(f"[Verbose] Model has {info['node_count']} nodes.")

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
