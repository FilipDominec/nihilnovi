![PlotCommander - file-oriented data plotting and manipulation](img/logo.png)

### Short description 
A lightweight application allowing to browse data files on your disk, and see their contents immediately plotted in the right panel.


Key points:
 * [x] Data file viewing, comparison and other simple tasks should be **as easy as browsing one's photo gallery**
 * [ ] Data preprocessing should **allow the flexibility of writing standalone scripts** in *[Python](https://www.python.org/)*+*[NumPy](http://www.numpy.org/)*
 * [ ] Plot options are determined by the **matplotlib library**, so that its [well-written documentation](http://matplotlib.org) and tricks apply. Settings can be also stored as python scripts.
 * [ ] **Program code is kept short** and as clean as possible to enable its reuse in other projects
 * [ ] Define **keyboard shortcuts** for all important functions. While easy to learn, mouse control of a program is slow. 
 * [x] **Promote open data formats** in research for easier cooperation, safer archivation and more efficient work. Rely on open-source libraries and make the program multi-platform.

### Motivation 
Scientific work is often based on handling numerical or experimental results in a computer. With the currently available options, it  can become a somewhat frustrating task, which people solve in different ways. One can store the data in a **proprietary structured formats** of specialized software; perhaps the most popular being "[Origin](http://originlab.com/) projects" \*.opj. The trouble with this approach is in that it permanently restricts the author and all their collaborators to use one piece of proprietary software, with compatibility issues between its versions and without any guarantee of being able to access your results after 10 or 20 years.

Switching to  alternative **open-source structured formats**, such as [Scidavis](http://scidavis.sourceforge.net/), may present a compatibility barrier, since its interoperability with Origin has been still questionable. In either case, the workflow remains limited to the capabilities of the corresponding program. It is said that holding a hammer, one sees every problem as a nail; likewise, using a graphical application with fairly limited capabilities and almost no means of automatization, a scientist wrongly perceives many interesting problems either as desperately tedious or even untreatable. Aside of this, such applications force the user to accept one given point-and-click workflow which may be far from optimal, and do not allow attaching arbitrary files to the datasets. Also the quality of the plots is not always good.

A different approach is to store one's data as plain **text files** (**\*.dat** or **\*.csv**). Fairly complex operations then can be programmed using, e.g., Matlab, R, Python or other suitable language, and gigantic amounts of data can be processed in a single batch. However, it is inconvenient to repeatedly write own scripts even for simple operations -- such as plotting or curve fitting. Sometimes people store the data along with **image files** with their plots, but again, the repeated plotting can be tedious.

**PlotCommander** resolves this problem by allowing the user to **view plain text files** rendered immediately as plots.

![a screenshot of the first test of the program](img/screenshot.png)

### Installation 

On Linux, you may need to get its dependencies; e.g. for Ubuntu 15.04/16.04, run:

    sudo apt-get install python3-matplotlib python3-numpy python3-gi-cairo

Then get the fresh version by pulling this project, and launch the program directly:

    git clone http://github.com/filipdominec/plotcommander.git
    cd plotcommander
    python3 plotcommander.py

### Other formats

In the future, seamless browsing of multiple-dataset files will probably bring also following dependencies

	## .OPJ - Origin files
	sudo apt-get install -y cython3 doxygen cmake libboost-all-dev
	git clone https://github.com/Saluev/python-liborigin2.git
	cd python-liborigin2/
	mkdir build
	cd build
	cmake ../
	make
	doxygen Doxyfile
	cd ..
	sudo python3 setup.py install
	cd ..

    ## .HDF5 - Hierarchical data format
    sudo apt-get install python3-h5py
    
	## .XLS - Excel files (and what about .ODS?)
    sudo apt-get install python3-xlrd


On Windows, the proposed distribution approach is to use [py2exe](http://py2exe.org/) to bundle all required dependencies into one package.

### Accepted file formats 
PlotCommander will try to understand all common formatting of *.dat (or, *.csv) files. A minimal example:

    column1 column2
    10		500
    20.5    345
    30      5.67e2

Running `./plotcommander.py test_files/minimal.dat` will open a window showing a two-segment line. If the first line cannot be interpreted as numbers, it will consider it a *header*, i.e. this plot will correctly recognize the x- and y-axis names.

Using the excel parser, it can also plot the first pair of columns (from the first sheet) XLS files. An example is in `./plotcommander.py test_files/xlstest.xls`.

### Reusable parts of the code (which may be useful for other projects)
#### Robust CSV parser
I tried to write a module that determines the number of columns in a text file and returns all data as a *numpy* array. Currently I believe it is more reliable than similar functions from pandas and numpy. 

#### Alpha-numeric sorting of files
Usual sorting algorithms do not care much about the numerical values embedded in a string.
This means e.g. that 'temperature-12' may wrongly come after 'temperature12', or '12200fish' will in 
most cases come after '0.123E+05fish'. For scientific data manipulation, this is not satisfactory.

The `sort_alpha_numeric.py` module offers the `sort_alpha_numeric()` function which accepts a list of strings. For each of them,
it uses a regular expression to split it into a sub-list of interleaved non-numeric and numeric sections, the 
latter being converted to true float numbers. Then, the proper order of these sub-lists can be efficiently found, 
and the original names are returned. 

To test the intelligent alpha-numeric sorting, try to call it add arguments as such:
```python3 sort_alpha_numeric.py xx-123.4zz xx-1.233e+002yy xx-123.2yy xx-123.4yy```

### PAQ - presumably asked questions
#### Q: Can I open Origin (\*.opj) files now?
A: Not yet, since *liborigin* needs to be translated to python3. I will try to fix it. 


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
 * [ ] plotcommander.py files should be searched for in the directory (and all updirs, too)
