import keras
import os
import random
import numpy as np
import cv2

# TODO use imgaug for more robust image augmentation
def preprocess_input(image, randomVals):
    '''
    performs data augmentations listed below each with chance == 50%
    - Horiontal flip
    - Random brightness +- 0.2
    - Random contrast +- 0.2
    - Random saturation +- 0.2
    - Hue Jitter +- 0.1

    all random values provided in range (0,1)
    '''
    if randomVals[0] > 0.5:
        # flip image horizontally
        #image = np.flip(image, 1)
        None
    if randomVals[1] > 0.5:
        # increase/ decrease contrast
        image = np.uint8(np.clip(image * (0.8 + randomVals[2]/2.5), a_min=0, a_max=255))
    # Convert image to HSV for some transformations
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int32)
    if randomVals[3] > 0.5:
        # change brightness of image
        hsv_image[:,:,2] += int(((randomVals[4]/2.5 )- 0.2 ) * 255.) 
        hsv_image[:,:,2] = np.clip(hsv_image[:,:,2], a_min =0, a_max = 255) 
    if randomVals[5] > 0.5:
        # change staturation
        hsv_image[:,:,1] += int(((randomVals[6]/2.5 )- 0.2 ) * 255.)
        hsv_image[:,:,1] = np.clip(hsv_image[:,:,1], a_min = 0, a_max = 255) 
    if randomVals[7] > 0.5:
        # change Hue
        hsv_image[:,:,0] += int(((randomVals[8]/2.5 )- 0.2 ) * 179.)
        hsv_image[:,:,0] = np.clip(hsv_image[:,:,0], a_min = 0, a_max = 179) 
    # Convert image back from HSV
    image = cv2.cvtColor(np.uint8(hsv_image), cv2.COLOR_HSV2BGR)
    return image


    #for x in range(0,9):
    #    randomVals.append(random.random())
    #input_img = preprocess_input(image=input_img, randomVals=randomVals)

class segmentationGenerator(keras.utils.Sequence):
    '''Generates data for Keras'''
    '''Framework taken from https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly'''
    '''Provided directories should contain the same number of files all with the same names to their pair image'''
    def __init__(self, img_dir, seg_dir, batch_size = 64, image_size=(640,192), shuffle=True, agumentations=True):
        self.img_dir = img_dir
        self.seg_dir = seg_dir
        self.image_size = image_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.agumentations = agumentations
        self.inputs = []
        self.initalSetup()

    def __len__(self):
        '''Denotes the number of batches per epoch'''
        return int(np.floor(len(self.inputs) / self.batch_size))


    def __getitem__(self, index):
        '''Generate one batch of data'''
        outX  =  np.empty((self.batch_size,  *self.image_size, 3))
        outY  =  np.empty((self.batch_size,  *self.image_size, 3))
        outY_0 = np.empty((self.batch_size, *self.image_size, 3))
        outY_1 = np.empty((self.batch_size, *self.image_size, 3))

        imageNames = self.inputs[index*self.batch_size:(index+1)*self.batch_size]

        for _, imageNameSet in enumerate(imageNames):
            img_path = os.path.join(self.img_dir, imageNameSet[0])
            seg_path = os.path.join(self.seg_dir, imageNameSet[0].replace('_', '_road_'))

            img_orig = cv2.imread(img_path)
            seg_orig = cv2.imread(seg_path)

            if (seg_orig is None):
                print("Error in seg path: " + seg_path)
                continue

            img = cv2.resize(img_orig, dsize=self.image_size)
            seg = cv2.resize(seg_orig, dsize=self.image_size)
            
            # print(img.shape)
            # cv2.imshow('test', img)
            # cv2.waitKey(-1)
            
            if self.agumentations:
                randomVals = []
                for x in range(0,9):
                    randomVals.append(random.random())
                img_augmented = preprocess_input(image=img, randomVals=randomVals)
            else:
                img_augmented = img

            outX[_]   =  np.transpose(img_augmented, axes=[1,0,2])
            # outY_0[_] =  np.transpose(img,           axes=[1,0,2])
            # outY_1[_] =  np.transpose(seg,           axes=[1,0,2])
            outY[_] =  np.transpose(seg,           axes=[1,0,2])

            #test_out = outX[_].astype('uint8')#np.transpose(left_augmented,     axes=[1,0,2])
            #cv2.imshow('test', test_out)
            #cv2.waitKey(-1)

            # outY = np.concatenate([outY_0,outY_1], axis=3)

        return outX, outY #[outY_0, outY_1, outY_2, outY_3]
                        

    def on_epoch_end(self):
        ''' Shuffle the data if that is required'''
        if self.shuffle:
            random.shuffle(self.inputs)   
    
    def initalSetup(self):
        #print("")
        imgs = os.listdir(self.img_dir)
        imgs.sort()

        segs = os.listdir(self.seg_dir)
        segs.sort()

        systemFiles = '.DS_Store'
        
        prefixes = ('.')
        for word in imgs[:]:
            if word.startswith(prefixes):
                imgs.remove(word)
            if word is systemFiles:
                imgs.remove(word)

        self.inputs = []

        for imgName in imgs:
            self.inputs.append([imgName])
                
        if self.shuffle:
            random.shuffle(self.inputs)   
        #self.inputs = self.inputs[0:100]   
        print("")
        print("")



if __name__ == "__main__":
    test = segmentationGenerator('data/data_road/training/image_2', 'data/data_road/training/gt_image_2/',   batch_size=8, shuffle=True)

    test.__getitem__(1)

    print('Data generator test success.')