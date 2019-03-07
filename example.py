import boto3

s3 = boto3.client('s3')


def main():
    buckets = s3.list_buckets()
    print(buckets.get('Buckets'))


if __name__ == "__main__":
    main()
