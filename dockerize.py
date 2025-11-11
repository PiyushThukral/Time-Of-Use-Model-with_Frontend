import os
import subprocess

def create_dockerfile(project_folder, image_name):
    dockerfile_content = f"""
    # Use the official Python image as a base
    FROM python:3.9-slim
    
    # Set the working directory in the container
    WORKDIR /app
    
    # Copy the project files to the container
    COPY . /app
    
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Default command to run when starting the container
    CMD ["python", "main.py"]
    """
    
    # Write the Dockerfile
    dockerfile_path = os.path.join(project_folder, "Dockerfile")
    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(dockerfile_content)
    print(f"Dockerfile created at {dockerfile_path}")

def build_docker_image(project_folder, image_name):
    # Build the Docker image
    subprocess.run(
        ["docker", "build", "-t", image_name, "."],
        cwd=project_folder,
        check=True
    )
    print(f"Docker image '{image_name}' built successfully.")

def run_docker_container(image_name, container_name):
    # Run the Docker container
    subprocess.run(
        ["docker", "run", "--name", container_name, image_name],
        check=True
    )
    print(f"Docker container '{container_name}' is running.")

# Main function
if __name__ == "__main__":
    project_folder = input("Enter the path to your project folder: ").strip()
    image_name = input("Enter the Docker image name: ").strip()
    container_name = input("Enter the Docker container name: ").strip()
    
    if not os.path.exists(project_folder):
        print("Error: The specified folder does not exist.")
        exit(1)
    
    if not os.path.isfile(os.path.join(project_folder, "requirements.txt")):
        print("Error: 'requirements.txt' not found in the specified folder.")
        exit(1)
    
    create_dockerfile(project_folder, image_name)
    build_docker_image(project_folder, image_name)
    run_docker_container(image_name, container_name)
