mkdir -p logs
python main.py --input_log ./model_logs/nasnet_cifar.log > nasnet_cifar.output 2>&1
python main.py --input_log ./model_logs/nasnet_imagenet_large.log > nasnet_imagenet_large.output 2>&1
python main.py --input_log ./model_logs/nasnet_imagenet_mobile.log > nasnet_imagenet_mobile.output 2>&1
python main.py --input_log ./model_logs/inception.log > inception.output 2>&1
python main.py --input_log ./model_logs/randwire.log > randwire.output 2>&1