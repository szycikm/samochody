import sys
import cv2
import numpy as np

from glob import glob
from os.path import splitext, basename, isfile
from src.utils import crop_region, image_files_from_folder
from src.drawing_utils import draw_label, draw_losangle, write2img
from src.label import lread, Label, readShapes
from pdb import set_trace as pause


def generate_output(output_dir, bname, original_frame_path, labels):

	YELLOW = (  0,255,255)
	RED = (  0,  0,255)
		
	output_str = '%s' % bname.replace('-', ':')
	original_frame = cv2.imread(original_frame_path)

	if labels:
		for i,label in enumerate(labels):
			lcar = label[0]
			lp_label = label[1]
			lp_str = label[2]
			draw_label(original_frame, lcar, color=YELLOW, thickness=3)
			
			if lp_label:
				Llp_shapes = readShapes(lp_label)
				pts = Llp_shapes[0].pts*lcar.wh().reshape(2, 1) + lcar.tl().reshape(2, 1)
				ptspx = pts*np.array(original_frame.shape[1::-1], dtype=float).reshape(2, 1)
				draw_losangle(original_frame, ptspx, RED,3)

				if lp_str:
					llp = Label(0,tl=pts.min(1),br=pts.max(1))
					write2img(original_frame,llp,lp_str)
					if len(lp_str) in range(6, 8):
						output_str += ',%s' % lp_str

	cv2.imwrite('%s/%s_output.png' % (output_dir,bname),I)
	if len(output_str.split(',')) > 1:
		# sys.stdout.write('%s\n' % output_str)
		return output_str
	
	return ''


