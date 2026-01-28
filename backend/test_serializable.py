
import json
import numpy as np

def _ensure_serializable(obj):
    """Recursively convert numpy types to python native types for JSON serialization"""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return [_ensure_serializable(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_ensure_serializable(x) for x in obj]
    return obj

def test():
    data = {
        "a": np.int64(42),
        "b": np.float32(3.14),
        "c": [np.int32(1), np.int32(2)],
        "d": {"nested": np.array([1, 2, 3])},
        "e": "normal string"
    }
    
    print("Original types:")
    print(f"a: {type(data['a'])}")
    
    clean = _ensure_serializable(data)
    
    print("\nCleaned types:")
    print(f"a: {type(clean['a'])}")
    print(f"b: {type(clean['b'])}")
    print(f"c[0]: {type(clean['c'][0])}")
    print(f"d['nested']: {type(clean['d']['nested'])}")
    
    try:
        json.dumps(clean)
        print("\nJSON Serialization: SUCCESS")
    except TypeError as e:
        print(f"\nJSON Serialization: FAILED ({e})")

if __name__ == "__main__":
    test()
