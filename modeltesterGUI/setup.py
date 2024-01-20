from setuptools import setup, find_packages
import os 

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory): 
         for filename in filenames: 
            paths.append(os.path.join(path, filename))
    print("Paths:", paths)
    return paths
models = package_files('src')


setup(
    name = 'modeltesterGUI', 
    version = '1.0.1',
    description = "Sample modeltesterGUI", 
    license = 'MIT',
    author='Debartha Chakraborty', 
    author_email='', 
    packages=find_packages('package'),
    package_dir={'': 'package'}, 
    package_data={"src.assets": ["*png", "*.ico"],
                  "src.weights": ["*.pt"]},
    include_package_data=True,
    keywords='Yolo', 
    install_requires=[
        'opencv_python',
        'Pillow',
        'psutil',
        'pywin32',
        'setuptools',
        'ttkbootstrap',
        'ultralytics',
    ],
    entry_points={'console_scripts': ['modeltesterGUI = src.run:main']},
    python_requires='>=3.6',
)