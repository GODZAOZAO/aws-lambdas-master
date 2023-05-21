Author: Luke Jordan 
Email: bruceli@vt.edu

Any time you want to compile your code for AWS Lambda, run:

    python generate_exportables_to_aws.py



Any time you used a new package, you must list that package in installed_packages.txt.
Then, you need to run 

    python generate_exportables_to_aws.py

But ensure that you tell the script to reinstall packages so that the zip files can update.



Add folders like delete-contact, get-fooditem, etc, and inside each folder include a lambda_function.py 
file. This is the standard for what AWS Lambda expects. See what I have as a reference.
