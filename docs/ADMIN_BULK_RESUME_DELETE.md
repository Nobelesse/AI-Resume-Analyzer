# Bulk resume deletion — administrator

On Admin → Resume Management, use individual row checkboxes or **Select all displayed resumes** to choose records. Filters apply, and the view supports up to 2,000 records. Review the selected count, check the acknowledgement, type `DELETE` and confirm. The API requires admin authorization, validates all IDs and performs one database transaction; analyses and job matches cascade. After commit, it removes the associated files from the upload directory. Deleting accounts is a separate operation. The action is irreversible without a backup.
