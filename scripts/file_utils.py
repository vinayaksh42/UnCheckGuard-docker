import os
import shutil

def delete_directory(directory):
    """Deletes the specified directory and all its contents."""
    if os.path.exists(directory):
        shutil.rmtree(directory)

def create_directory(directory):
    """Creates the specified directory if it does not already exist."""
    os.makedirs(directory, exist_ok=True)

def delete_directory_contents(directory):
    """Deletes all contents inside the specified directory without removing the directory itself."""
    if os.path.exists(directory) and os.path.isdir(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

def copy_directory(src, dst):
    """Copies the entire directory from src to dst."""
    if os.path.exists(src) and os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)

def copy_file(src_file, dst_file):
    """Copies a specific file from src_file to dst_file."""
    if os.path.exists(src_file) and os.path.isfile(src_file):
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)

def copy_jars_only(pom_dir, dep_to_copy):
    # Copy dependencies from 'target/dependency' to dep_new_dir
    dependency_src = os.path.join(pom_dir, "target", "dependency")
    create_directory(dep_to_copy)
    copy_directory(dependency_src, dep_to_copy)