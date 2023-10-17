# step1: Recognize
python videoclipper.py --stage 1 \
                       --file ../examples/2022云栖大会_片段.mp4 \
                       --sd_switch yes \
                       --output_dir ./output
# now you can find recognition results and entire SRT file in ./output/
# step2: Clip
python videoclipper.py --stage 2 \
                       --file ../examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output \
                       --dest_text '所以这个是我们办这个奖的初心啊，我们也会一届一届的办下去' \
                    #    --dest_spk spk0 \
                       --start_ost 0 \
                       --end_ost 100 \
                       --output_file './output/res.mp4'