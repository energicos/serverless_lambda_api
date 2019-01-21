# remove all existing zip files
rm *.zip

# create-table-rds
cd create-table-rds
zip -r ../create-table-rds.zip *
cd ..
aws s3 cp create-table-rds.zip s3://tests3-s3bucket-t9ne2v3mb47y

# get-all-accounts
cd get-all-accounts
zip -r ../get-all-accounts.zip *
cd ..
aws s3 cp get-all-accounts.zip s3://tests3-s3bucket-t9ne2v3mb47y

# search-accounts
cd search-accounts
zip -r ../search-accounts.zip *
cd ..
aws s3 cp search-accounts.zip s3://tests3-s3bucket-t9ne2v3mb47y

# update-accounts
cd update-accounts
zip -r ../update-accounts.zip *
cd ..
aws s3 cp update-accounts.zip s3://tests3-s3bucket-t9ne2v3mb47y

# delete-accounts
cd delete-accounts
zip -r ../delete-accounts.zip *
cd ..
aws s3 cp delete-accounts.zip s3://tests3-s3bucket-t9ne2v3mb47y

