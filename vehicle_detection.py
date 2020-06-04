import sys
import cv2
import numpy as np
import traceback
import darknet.python.darknet as dn

from src.label import Label, lwrite
from os.path import splitext, basename, isdir
from os import makedirs
from src.utils import crop_region, image_files_from_folder
from darknet.python.darknet import detect, detect_2_0

def vehicle_detect(img_path, vehicle_net, vehicle_meta, vehicle_threshold):
	detected, _ = detect(vehicle_net, vehicle_meta, img_path ,thresh=vehicle_threshold)

	detected = [r for r in detected if r[0] in ['car','bus']]

	print('\t\t%d cars found' % len(detected))

	Lcars = []
	Icars = []
	if len(detected):
		Iorig = cv2.imread(img_path)
		WH = np.array(Iorig.shape[1::-1],dtype=float)

		print('\t\t%d cars found' % len(detected))

		for i,r in enumerate(detected):
			cx,cy,w,h = (np.array(r[2])/np.concatenate((WH,WH))).tolist()
			tl = np.array([cx - w/2., cy - h/2.])
			br = np.array([cx + w/2., cy + h/2.])
			label = Label(0, tl, br)
			Icar = crop_region(Iorig,label)

			Lcars.append(label)

			cv2.imwrite('%s/%s_%dcar.png' % (output_dir, bname, i), Icar)
			Icars.append(Icar)

		#lwrite('%s/%s_cars.txt' % (output_dir,bname), Lcars)
	return Icars, Lcars


if __name__ == '__main__':
	try:
		input_dir = sys.argv[1]
		output_dir = sys.argv[2]

		vehicle_threshold = .5

		vehicle_weights = 'data/vehicle-detector/yolo-voc.weights'
		vehicle_netcfg = 'data/vehicle-detector/yolo-voc.cfg'
		vehicle_dataset = 'data/vehicle-detector/voc.data'

		vehicle_net = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
		vehicle_meta = dn.load_meta(vehicle_dataset)

		imgs_paths = image_files_from_folder(input_dir)
		imgs_paths.sort()

		if not isdir(output_dir):
			makedirs(output_dir)

		print('Searching for vehicles using YOLO...')

		for i,img_path in enumerate(imgs_paths):
			print('\tScanning %s' % img_path)

			bname = basename(splitext(img_path)[0])

			detected, _ = detect(vehicle_net, vehicle_meta, img_path ,thresh=vehicle_threshold)

			detected = [r for r in detected if r[0] in ['car','bus']]

			print('\t\t%d cars found' % len(detected))

			if len(detected):
				Iorig = cv2.imread(img_path)
				WH = np.array(Iorig.shape[1::-1],dtype=float)
				Lcars = []

				for i,r in enumerate(detected):
					cx,cy,w,h = (np.array(r[2])/np.concatenate((WH,WH))).tolist()
					tl = np.array([cx - w/2., cy - h/2.])
					br = np.array([cx + w/2., cy + h/2.])
					label = Label(0, tl, br)
					Icar = crop_region(Iorig,label)

					Lcars.append(label)

					cv2.imwrite('%s/%s_%dcar.png' % (output_dir, bname, i), Icar)

				lwrite('%s/%s_cars.txt' % (output_dir,bname), Lcars)
	except:
		traceback.print_exc()
		sys.exit(1)

	sys.exit(0)