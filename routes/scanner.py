from flask import Blueprint, request, jsonify
import os

scanner_bp = Blueprint('scanner', __name__)

def build_dir_tree(path, current_depth=0, max_depth=3):
    # Ignore heavy or hidden folders to avoid performance issues
    EXCLUDE_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.idea', '.vscode'}
    
    if current_depth > max_depth:
        return {"name": "... (depth limit reached)", "type": "directory", "children": []}
        
    try:
        name = os.path.basename(path) or path
        if os.path.isfile(path):
            return {"name": name, "type": "file", "size": os.path.getsize(path)}
            
        children = []
        # Sort so folders come first, then files
        items = sorted(os.listdir(path))
        
        for item in items:
            if item in EXCLUDE_DIRS:
                continue
                
            item_path = os.path.join(path, item)
            try:
                if os.path.isdir(item_path):
                    children.append(build_dir_tree(item_path, current_depth + 1, max_depth))
                else:
                    children.append({
                        "name": item,
                        "type": "file",
                        "size": os.path.getsize(item_path)
                    })
            except (PermissionError, FileNotFoundError):
                # Add a dummy node indicating permission issue/missing file
                children.append({
                    "name": f"{item} (access denied)",
                    "type": "error"
                })
                
        return {
            "name": name,
            "type": "directory",
            "children": children
        }
    except PermissionError:
        raise PermissionError(f"Permission denied to access directory: {path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory not found: {path}")
    except Exception as e:
        raise Exception(f"Failed to scan directory: {str(e)}")

@scanner_bp.route('/api/scan', methods=['POST'])
def scan_directory():
    try:
        data = request.json or {}
        input_path = data.get('path', '').strip()
        
        # Default path is the current workspace (where the flask app is)
        if not input_path:
            input_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Resolve to absolute path
        abs_path = os.path.abspath(input_path)
        
        # Error handling validations
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"The path '{input_path}' does not exist on the server.")
            
        if not os.path.isdir(abs_path):
            raise NotADirectoryError(f"The path '{input_path}' is a file, not a directory.")
            
        # Verify permissions or read contents
        try:
            items = os.listdir(abs_path)
        except PermissionError:
            raise PermissionError(f"Permission denied: Accessing '{input_path}' is restricted.")
            
        # Check if empty folder
        if len(items) == 0:
            return jsonify({
                "success": True,
                "path": abs_path,
                "is_empty": True,
                "message": f"The directory is empty: '{input_path}'",
                "tree": {
                    "name": os.path.basename(abs_path) or abs_path,
                    "type": "directory",
                    "children": []
                }
            })
            
        # Build tree structure
        tree = build_dir_tree(abs_path)
        
        return jsonify({
            "success": True,
            "path": abs_path,
            "is_empty": False,
            "tree": tree
        })
        
    except FileNotFoundError as e:
        return jsonify({"success": False, "error_type": "FileNotFoundError", "error": str(e)}), 404
    except NotADirectoryError as e:
        return jsonify({"success": False, "error_type": "NotADirectoryError", "error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"success": False, "error_type": "PermissionError", "error": str(e)}), 403
    except Exception as e:
        return jsonify({"success": False, "error_type": "Exception", "error": str(e)}), 500
