mkdir .tmp
cd ./.tmp
mplayer -tv device=/dev/video0:width=640:height=480:driver=v4l2:input=2:norm=pal:fps=25 tv://1 -aspect 4:3 -vo jpeg