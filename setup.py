from setuptools import setup

package = 'executing_node'


setup(name=package,
      version='0.1.0',
      description='Get the currently executing AST node of a frame',
      url='https://github.com/alexmojaki/' + package,
      author='Alex Hall',
      author_email='alex.mojaki@gmail.com',
      license='MIT',
      py_modules=[package],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      zip_safe=False)
