I've left the folder in the shape I found it. Feel free to organize it better, also you will most likely only need a tiny fraction of everything.

As for the programming, I guess it will at most serve as inspiration how to use the Guppy with pymba and how to include it in acquire. . It's as you can see beginners work


The most important files are in the folder siscam:

AVTcam.py provides some custom-made classes that facilitate the use of the pymba-classes in acquire. Maybe you can move these definitions acquire to simplify things. It's some kind of intermediate layer that one maybe doesn't even need.

Acquire-modified.py is the version I worked on. I tried to document extensively what I did (but maybe partly in German). If you search for #AVT you should find everything you need. However it is not really in a clean state. After starting to work on the cavities I kind of abandonned this project, and that's what it looks like.

In cam.py I don't recall changing anything to make it work.


In the folder pymba-siscam-interface you find three different versions of acquire-modified.py, with minor differences. I think the most recent one crashes. The file Guppy-feature-list.txt maybe useful. 

The folder Allied Vision Technologies contains mainly stuff for the other APIs of Vimba. 

Edcam is the program Sebastien was using on the new experiment.


Have fun and let me know if you have any questions