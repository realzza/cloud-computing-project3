kubectl delete --ignore-not-found=true configmap pyfile
kubectl delete --ignore-not-found=true configmap outputkey

kubectl create configmap pyfile --from-file pyfile=serverless_handler.py --output yaml >pyfile.yaml
kubectl create configmap outputkey --from-literal REDIS_OUTPUT_KEY=zz188-proj3-output --output yaml >outputkey.yaml