import numpy as np

# Make sure that caffe is on the python path:
import sys 
CAFFE_HOME = '/home/ubuntu/caffe/' # CHANGE THIS LINE TO YOUR Caffe PATH
sys.path.insert(0, CAFFE_HOME + 'python')

import caffe

# Set the right path to your model definition file, pretrained model weights,
# and the image you would like to classify.
MODEL_FILE = CAFFE_HOME + 'models/bvlc_reference_caffenet/deploy.prototxt'
PRETRAINED = CAFFE_HOME + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel' #Weights to be used w/MODEL_FILE
IMAGE_FILE1 = CAFFE_HOME + 'examples/images/cat.jpg'
IMAGE_FILE2 = CAFFE_HOME + 'examples/images/fish-bike.jpg'

# Download weight file if not found
import os
if not os.path.isfile(PRETRAINED):
    print("Downloading pre-trained CaffeNet model...")
    os.system('../scripts/download_model_binary.py ../models/bvlc_reference_caffenet')

# Use GPU or CPU
caffe.set_mode_cpu()
#caffe.set_mode_gpu()

# Load network
# Note arguments to preprocess input
#  mean subtraction switched on by giving a mean array
#  input channel swapping takes care of mapping RGB into the reference ImageNet model's BGR order
#  raw scaling multiplies the feature scale from the input [0,1] to the ImageNet model's [0,255]
net = caffe.Classifier(MODEL_FILE, PRETRAINED,
                       mean=np.load(CAFFE_HOME + 'python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1),
                       channel_swap=(2,1,0),
                       raw_scale=255,
                       image_dims=(256, 256))
# Alternatively, the above could have been written as:
#net = caffe.Classifier(MODEL_FILE, PRETRAINED)
#net.transformer.set_mean('data', np.load(CAFFE_HOME + 'python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1))
#net.transformer.set_raw_scale('data', 255)  # reference model operates on [0,255] range instead of [0,1]
#net.transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

input_image1 = caffe.io.load_image(IMAGE_FILE1)
input_image2 = caffe.io.load_image(IMAGE_FILE2)
input_images = [input_image1, input_image2]

# Classify image
prediction = net.predict(input_images)  # predict takes any number of images, and formats them for the Caffe net automatically
print 'predicted classes:', prediction[0].argmax(), prediction[1].argmax()

### The steps below are OPTIONAL ###
# View input_image1
plt.imshow(input_image1)

# View the probabilities of all the classes for input_image1 as a bar chart
plt.plot(prediction[0])

# Time the full pipeline classification for 1 image w/oversampling
timeit net.predict([input_image1])

# Time the only forward pass classification for 1 image by resizing/oversampling before forward pass
#   Resize the image to the standard (256, 256) and oversample net input sized crops.
input_oversampled = caffe.io.oversample([caffe.io.resize_image(input_image1, net.image_dims)], net.crop_dims)
#   'data' is the input blob name in the model definition, so we preprocess for that input.
caffe_input = np.asarray([net.transformer.preprocess('data', in_) for in_ in input_oversampled])
#  forward() takes keyword args for the input blobs with preprocessed input arrays.
timeit net.forward(data=caffe_input)
