import numpy as np


class SquareCam:
    # ###########################################################################
    #                       Initialization of the object.                      #
    ############################################################################
    def __init__(self, pixVals, pic_size=54):
        self.patches = []
        self.pixNumArr = []

        self.pixSideLength = 1.0 * np.sqrt(2)
        self.numCamSpirals = 13
        self.pos = np.zeros((len(pixVals), 2))
        self.pixVals = np.array(pixVals)
        self.buildSquareCamera()
        self.build_oversampled_camera(pic_size)
        self.pic_size = pic_size

    ############################################################################
    #                         Generate the VERITAS camera pixel positions.     #
    ############################################################################
    def load_pixVal(self, pixVals):
        self.pixVals = np.array(pixVals)

    def buildSquareCamera(self):
        self.patches = []
        self.pixNumArr = []

        pixNum = 1
        self.pixNumArr.append(pixNum)
        pixNumStr = "%d" % pixNum

        self.pos[0, 0] = 0.
        self.pos[0, 1] = 0.

        deltaX = self.pixSideLength * np.sqrt(2) / 2.
        deltaY = self.pixSideLength * np.sqrt(2)

        for spiral in range(1, self.numCamSpirals + 1):

            xPos = 2. * float((spiral)) * deltaX
            yPos = 0.

            # For the two outermost spirals, there is not a pixel in the y=0 row.
            if spiral < 12:
                pixNum += 1
                self.pixNumArr.append(pixNum)
                pixNumStr = "{:d}".format(pixNum)
                #plt.text(xPos+self.textOffsetX*(math.floor(math.log10(pixNum)+1.)), yPos+self.textOffsetY, pixNum, size=self.pixLabelFontSize)

                self.pos[pixNum - 1, 0] = xPos
                self.pos[pixNum - 1, 1] = yPos

            nextPixDir = np.zeros((spiral * 6, 2))
            skipPixel = np.zeros((spiral * 6, 1))

            for y in range(spiral * 6 - 1):
                # print "%d" % (y/spiral)
                if (y / spiral < 1):
                    nextPixDir[y, :] = [-1, -1]
                elif (y / spiral >= 1 and y / spiral < 2):
                    nextPixDir[y, :] = [-2, 0]
                elif (y / spiral >= 2 and y / spiral < 3):
                    nextPixDir[y, :] = [-1, 1]
                elif (y / spiral >= 3 and y / spiral < 4):
                    nextPixDir[y, :] = [1, 1]
                elif (y / spiral >= 4 and y / spiral < 5):
                    nextPixDir[y, :] = [2, 0]
                elif (y / spiral >= 5 and y / spiral < 6):
                    nextPixDir[y, :] = [1, -1]


            # The two outer spirals are not fully populated with pixels.
            # The second outermost spiral is missing only six pixels (one was excluded above).
            if (spiral == 12):
                for i in range(1, 6):
                    skipPixel[spiral * i - 1] = 1
            # The outmost spiral only has a total of 36 pixels.  We need to skip over the
            # place holders for the rest.
            if (spiral == 13):
                skipPixel[0:3] = 1
                skipPixel[9:16] = 1
                skipPixel[22:29] = 1
                skipPixel[35:42] = 1
                skipPixel[48:55] = 1
                skipPixel[61:68] = 1
                skipPixel[74:77] = 1

            for y in range(spiral * 6 - 1):

                xPos += nextPixDir[y, 0] * deltaX
                yPos += nextPixDir[y, 1] * deltaY

                if skipPixel[y, 0] == 0:
                    pixNum += 1
                    self.pixNumArr.append(pixNum)
                    pixNumStr = "%d" % pixNum
                    self.pos[pixNum - 1, 0] = xPos
                    self.pos[pixNum - 1, 1] = yPos

    def build_oversampled_camera(self, pic_size=54):
        camera = self
        pixel_size = camera.pixSideLength / np.sqrt(2)
        posx = camera.pos[:, 0]
        posy = camera.pos[:, 1]
        if (max(np.max(posx) * 2, np.max(posy) * 2) + 1) > pic_size:
            print('Picture size smaller than camera size. Set to default pic_size: {}.'.format(54))
            pic_size = 54
        posx_shift = posx + pic_size/2.+pixel_size/2. - 1
        posy_shift = posy + pic_size/2.+pixel_size/2. - 1
        camera.index = np.zeros((2,len(self.pixVals),4),dtype='int')
        for i,(x,y) in enumerate(zip(posx_shift,posy_shift)):
           x_L = int(round(x+pixel_size/2.))      
           x_S = int(round(x-pixel_size/2.))      
           y_L = int(round(y+pixel_size/2.))      
           y_S = int(round(y-pixel_size/2.))      
           camera.index[0,i,:] = np.array([x_L,x_S,x_S,x_L],dtype='int') 
           camera.index[1,i,:] = np.array([y_L,y_S,y_L,y_S],dtype='int') 

    def get_simple_oversampled_image(self):
        pic_size = self.pic_size
        image = np.zeros((pic_size, pic_size))
        index_x = self.index[0]
        index_y = self.index[1]

        pix     = self.pixVals/4.
        for x,y,value in zip(index_x,index_y,pix):
            image[x[0],y[0]] = value
            image[x[1],y[1]] = value
            image[x[2],y[2]] = value
            image[x[3],y[3]] = value

        return image
