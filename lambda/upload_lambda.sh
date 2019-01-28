BucketName=$1

# remove all existing zip files
rm *.zip

# create-table-rds
cd create-table-rds
zip -r ../create-table-rds.zip *
cd ..
aws s3 cp create-table-rds.zip s3://${BucketName}

# get-all-accounts
cd get-all-accounts
zip -r ../get-all-accounts.zip *
cd ..
aws s3 cp get-all-accounts.zip s3://${BucketName}

# search-accounts
cd search-accounts
zip -r ../search-accounts.zip *
cd ..
aws s3 cp search-accounts.zip s3://${BucketName}

# update-accounts
cd update-accounts
zip -r ../update-accounts.zip *
cd ..
aws s3 cp update-accounts.zip s3://${BucketName}

# delete-accounts
cd delete-accounts
zip -r ../delete-accounts.zip *
cd ..
aws s3 cp delete-accounts.zip s3://${BucketName}

