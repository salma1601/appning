import os
import glob
from sammba.registration import template_registrator
from sammba.externals.nipype.caching import Memory
from sammba.registration.base import compute_brain_mask, _bias_correct
from sammba.interfaces.segmentation import MathMorphoMask
from sammba.externals.nipype.utils.filemanip import fname_presuffix


anat_files = glob.glob(os.path.expanduser(
    '~/mrm_bil2_transformed/correct_headers/bil2_transfo_C57*.nii.gz'))
output_dir = os.path.expanduser('~/mrm_bil2_transformed_corrected_preprocessed')

# Corrected header
template_file = os.path.expanduser(
    '~/nilearn_data/mrm_2010/correct_headers/Average_template_invivo_corrected.nii.gz')
template_brain_mask_file = os.path.expanduser(
    '~/nilearn_data/mrm_2010/correct_headers/Average_brain_mask_invivo_corrected.nii.gz')
for anat_file in anat_files:
    registrator = template_registrator.TemplateRegistrator(
        brain_volume=400,
        dilated_template_mask=None,
        output_dir=output_dir,
        template=template_file,
        caching=True,
        template_brain_mask=template_brain_mask_file,
        registration_kind='affine')

    write_dir = os.path.join(output_dir, 'custom_masks')
    memory = Memory(write_dir)
    mm = memory.cache(MathMorphoMask)
    if 'Bj1' in anat_file:
        brain_mask_file = compute_brain_mask(
            anat_file, 400, os.path.join(output_dir, 'custom_masks'), bias_correct=False,
            caching=True)
        registrator.fit_anat(anat_file, brain_mask_file=brain_mask_file)
    elif  'Xx1' in anat_file:
        out_mm = mm(
            in_file=anat_file, volume_threshold=400, intensity_threshold=1900,
            out_file=fname_presuffix(anat_file, newpath=write_dir, suffix='_brain_mask'))
        registrator.fit_anat(anat_file, brain_mask_file=out_mm.outputs.out_file)
    elif 'y11' in anat_file:
        n4_file = _bias_correct(anat_file, write_dir=write_dir, caching=True)
        out_mm = mm(
            in_file=n4_file, volume_threshold=400, intensity_threshold=900,
            out_file=fname_presuffix(n4_file, newpath=write_dir, suffix='_brain_mask'))
        registrator.fit_anat(anat_file, brain_mask_file=out_mm.outputs.out_file)
    else:
        registrator.fit_anat(anat_file)
