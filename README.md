![Gayplot - File-Oriented data Plotting And Manipulation](img/logo.png)

### Short description 
A lightweight application allowing to browse data files on your disk, and see their contents immediately plotted in the right panel.


Key points:
 * Data file viewing, comparison and other simple tasks should be **as easy as browsing one's photo gallery**
 * Data preprocessing should **allow the flexibility of writing standalone scripts** in *[Python](https://www.python.org/)*+*[NumPy](http://www.numpy.org/)*
 * Plot options are determined by the **matplotlib library**, so that its [well-written documentation](http://matplotlib.org) and tricks apply. Settings can be also stored as python scripts.
 * Keep the **program code reusable**, i.e., as short and clean as possible.
 * Define **keyboard shortcuts** for all important functions. While easy to learn, mouse control of a program is slow. 
 * **Promote open data formats** in research for easier cooperation, safer archivation and more efficient work. Rely on open-source libraries and make the program multi-platform.

### Motivation 
Scientific work is often based on handling numerical or experimental results in a computer. With the currently available options, it  can become a somewhat frustrating task, which people solve in different ways. One can store the data in a **proprietary structured formats** of specialized software; perhaps the most popular being "[Origin](http://originlab.com/) projects" \*.opj. The trouble with this approach is in that it permanently restricts the author and all their collaborators to use one piece of proprietary software, with compatibility issues between its versions and without any guarantee of being able to access your results after 10 or 20 years.

Switching to  alternative **open-source structured formats**, such as [Scidavis](http://scidavis.sourceforge.net/), may present a compatibility barrier, since its interoperability with Origin has been still questionable. In either case, the workflow remains limited to the capabilities of the corresponding program. It is said that holding a hammer, one sees every problem as a nail; likewise, using a graphical application with fairly limited capabilities and almost no means of automatization, a scientist wrongly perceives many interesting problems either as desperately tedious or even untreatable. Aside of this, such applications force the user to accept one given point-and-click workflow which may be far from optimal, and do not allow attaching arbitrary files to the datasets. Also the quality of the plots is not always good.

A different approach is to store one's data as plain **text files** (**\*.dat** or **\*.csv**). Fairly complex operations then can be programmed using, e.g., Matlab, R, Python or other suitable language, and gigantic amounts of data can be processed in a single batch. However, it is inconvenient to repeatedly write own scripts even for simple operations -- such as plotting or curve fitting. Sometimes people store the data along with **image files** with their plots, but again, the repeated plotting can be tedious.

**GayPlot** resolves this problem by allowing the user to **view plain text files** rendered immediately as plots.

![a screenshot of the first test of the program](img/screenshot.png)

### Installation 

On Linux, you may need to get its dependencies; e.g. for Ubuntu 15.04/16.04, run:

    sudo apt-get install python3-matplotlib python3-pip python3-numpy python3-gi-cairo 

Then get the fresh version by pulling this project, and launch the program directly:

    git clone http://github.com/filipdominec/gayplot.git
    cd gayplot
    python3 gayplot.py

In the future, seamless browsing of multiple-dataset files will depend also on:

    ## LibHDF
    sudo apt-get install python-h5py
    
	## LibOrigin for python
	sudo apt-get install -y python-pip cython doxygen cmake libboost-all-dev
	pip install Cython
	git clone https://github.com/Saluev/python-liborigin2.git
	cd python-liborigin2/
	mkdir build
	cd build
	cmake ../
	make
	doxygen Doxyfile
	cd ..
	sudo python setup.py install
	cd ..

On Windows, the proposed distribution approach is to use [py2exe](http://py2exe.org/) to bundle all required dependencies into one package.

### Accepted file formats 
GayPlot will try to understand all common formatting of *.dat (or, *.csv) files. A minimal example:

    10      123
    20.5    345
    30      5.67e2

Running `./gayplot.py minimal.dat` will open a window showing a two-segment line.

### PAQ - presumably asked question
#### "Gayplot" - why did you choose this name?
By default, the program uses a sequential color coding for curve plotting that resembles the rainbow [LGBT flag](https://en.wikipedia.org/wiki/LGBT). However, it can be used by the heterosexual majority, too.


### To-Do 

 * [ ] add kb shortcuts - e.g. ctrl+w to close app, Matplotlib operations on the plot, ...
 * [ ] allow selecting curves in the file list (reuse FDMeasurementRecords.py)
 * [ ] allow selecting curves in the plot panel, too
 * [ ] data manipulation operations (shift x/y, zoom x/y, fit linear/gaussian/sine), file saving
 * [ ] when parameters encoded in file name: intelligent extraction of the changing parameter
 * [ ] multiple columns in files --> subfigures
 * [ ] merge functions from python-meep-utils:multiplot.py
 * [ ] use icons for the file/directory/dataset identification
 * [ ] enable browsing directories, dynamic unpacking sub-dirs and changing to up-dirs
 * [ ] enable browsing origin files if liborigin available for python3
 * [ ] enable browsing HDF5 files if libhdf available (dtto)
 * [ ] gayplotrc.py files should be searched for in the directory (and all updirs, too)
