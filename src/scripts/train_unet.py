from src.models.unet.network import get_unet
from src.processing.sat_images import segmentation_generator
from keras.callbacks import ModelCheckpoint, LearningRateScheduler


if __name__ == '__main__':
    data_gen_args = dict(rotation_range=0.2,
                         width_shift_range=0.05,
                         height_shift_range=0.05,
                         shear_range=0.05,
                         zoom_range=0.05,  # Note Curious of the one for sat images
                         horizontal_flip=True,
                         fill_mode='nearest')

    myGene = segmentation_generator(1, 'data/spacenet/rasters/', 'jpg', 'mask', data_gen_args, save_to_dir=None)

    model = get_unet()
    model_checkpoint = ModelCheckpoint('unet_membrane.hdf5', monitor='loss', verbose=1, save_best_only=True)
    model.fit_generator(myGene, steps_per_epoch=10, epochs=10, callbacks=[model_checkpoint])
