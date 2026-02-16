# Python Virtual Environment

### What is a Python Virtual Environment?

  - A virtual environment in Python is an isolated environment on the local machine, where we can run and test your Python projects.

### What it will does? 

  - Has its own Python interpreter.
  - Has its own set of installed packages.
  - Is isolated from other virtual environments.
  - Can have different versions of the same package

### Why virtual Environment useful?

Using virtual environments is important because:

  - It prevents package version conflicts between projects.
  - Makes projects more portable and reproducible.
  - Keeps your system Python installation clean.
  - Allows testing with different Python versions.

### Commands

**Verify Python Installation**
Before creating a virtual environment, verify that Python is installed:

```
python --version
```

**1.  Create Virtual Enviornment**

````
python -m venv env_name
````

Example:
````
python -m venv myenv
````

**2.  Activate Virtual Environment**

````
env_name/Scripts/activate
````
Example:

````
myenv\Scripts\activate
````
After activation, you will see: 

```
(myenv) c:/my_laptop/projects/
```
**3.  Deactivate Virtual Environment**

```
deactivate
```

**4.  Install Packages**

```
pip install package_name
```

**5.  Save Dependencies (requirements.txt)**

```
pip freeze > requirements.txt
```
**6.  Install from requirements.txt**

```
pip install -r requirements.txt
```

**7.  Delete Virtual Environment**

Simply delete the folder:
```
rmdir /s myenv      # Windows
```
**8.  Upgrade pip**

```
python -m pip install --upgrade pip
```

