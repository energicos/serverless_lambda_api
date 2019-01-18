cd create-table-rds
zip -r ../create-table-rds.zip *
cd ..
aws s3 cp create-table-rds.zip s3://tests3-s3bucket-t9ne2v3mb47y
