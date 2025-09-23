import subprocess as sb
import os
import datetime

class render_povray():
    def __init__(self,infile,outfile,paksize,tilesize_x=1,tilesize_y=1,tilesize_z=1,winter=0,make_front=0,pakstr="pak128japan",diagonal=0):
        self.infile=infile
        self.outfile=outfile
        self.paksize=int(paksize)
        self.Nx=int(tilesize_x)
        self.Ny=int(tilesize_y)
        self.Nz=int(tilesize_z)
        self.winter=int(winter)
        self.make_front=int(make_front)
        self.pakstr=pakstr
        self.diagonal = int(diagonal)
    def flag(self):
        def write_dat(outfile,pngname):
            dat_direc=[
                #straight
                ["",0,0,True],
                ["",0,3,True],
                ["",2,0,True],
                ["",1,3,True],
                ["",1,0,True],
                ["",2,3,True],
                ["",3,0,True],
                ["",3,3,True],
                ["",0,2,True],
                ["",0,1,True],
                ["",1,2,True],
                ["",2,1,True],
                ["",2,2,True],
                ["",1,1,True],
                ["",3,2,True],
                ["",3,1,True],
                #diagonal (v)
                ["_h",0,2,True],
                ["_v",0,3,True],
                ["_h",2,2,True],
                ["_v",2,3,True],
                ["_h",1,2,True],
                ["_v",1,3,True],
                ["_h",3,2,True],
                ["_v",3,3,True],
                ["_v",0,1,True],
                ["_h",0,0,True],
                ["_v",1,1,True],
                ["_h",1,0,True],
                ["_v",2,1,True],
                ["_h",2,0,True],
                ["_v",3,1,True],
                ["_h",3,0,True],
                #diagonal (h)
                ["_v",0,0,False],
                ["_h",0,3,False],
                ["_v",2,0,False],
                ["_h",2,3,False],
                ["_v",1,0,False],
                ["_h",1,3,False],
                ["_v",3,0,False],
                ["_h",3,3,False],
                ["_h",0,1,True],
                ["_v",0,2,True],
                ["_h",1,1,True],
                ["_v",1,2,True],
                ["_h",2,1,True],
                ["_v",2,2,True],
                ["_h",3,1,True],
                ["_v",3,2,True]
            ]
            max_int = 16+self.diagonal*32
            pngname=os.path.basename(pngname)[:-4]
            with open(outfile,mode="a") as f:
                if(self.winter+self.make_front==0):
                    f.write("\n\n\n\ndims=1,1,"+str(max_int)+"\n")
                if(self.make_front==0):
                    for i in range(max_int):
                        f.write("BackImage["+str(i)+"][0][0][0][0]["+str(self.winter)+"]="+pngname+dat_direc[i][0]+"."+str(dat_direc[i][1])+"."+str(dat_direc[i][2])+"\n")
                else:
                    for i in range(max_int):
                        f.write("FrontImage["+str(i)+"][0][0][0][0]["+str(self.winter)+"]="+pngname+dat_direc[i][0]+"_front"+"."+str(dat_direc[i][1])+"."+str(dat_direc[i][2])+"\n")
        def declare_povray(param,input_str):
            return "#declare "+str(param)+"="+str(input_str)+";\n"
        def rendering(pattern):
            pattern_str=""
            if pattern==1:
                pattern_str="_h"
            if pattern==2:
                pattern_str="_v"            
            if self.paksize%4==0:
                # filesize define
                Width=self.paksize*(max(self.Nx,self.Ny))*4
                Height=self.paksize*(max(self.Nx,self.Ny,self.Nz//2))*5
                # make inc file which defines some values. 
                temp_inc_filepath=os.path.dirname(self.infile)+"/temp.inc"
                with open(temp_inc_filepath,mode="w") as f:
                    f.write(declare_povray("int_x",self.Nx))
                    f.write(declare_povray("int_y",self.Ny))
                    f.write(declare_povray("int_z",max(self.Nz,1)))
                    f.write(declare_povray("number_width",max(self.Nx,self.Ny)))
                    f.write(declare_povray("number_hight",max(self.Nx,self.Ny,self.Nz//2)))
                    f.write(declare_povray("winter",self.winter))
                    f.write(declare_povray("make_front_image",self.make_front))
                    f.write(declare_povray("pak_str",'"'+self.pakstr+'"'))
                    f.write(declare_povray("diagonal_param",pattern))
                # rendering
                outname=self.outfile[:-4]+pattern_str
                if outname=="":
                    outname=self.infile[:-4]+pattern_str
                if self.make_front == 1:
                    outname+="_front"
                if self.winter==1:
                    outname+="-winter"
                try:
                    sb.run(["pvengine.exe","/NR","/EXIT","/RENDER",str(self.infile),"Width="+str(Width),"Height="+str(Height),"Antialias=Off","+O"+outname])
                except:
                    try:
                        sb.run(["povray",str(self.infile),"Width="+str(Width),"Height="+str(Height),"Antialias=Off","+O"+outname])
                    except:
                        return False
                if os.path.isfile(outname+".png")==False:
                    return False
                elif os.path.isfile(outname+"_0.png"):
                    t_1=os.path.getmtime(outname+".png")
                    t_2=os.path.getmtime(outname+"_0.png")
                    if (t_1<t_2):
                        return False
                    else:
                        return True
                else:
                    return True
            else:
                return False
        if not rendering(pattern=0):
            return False
        if self.diagonal==0:
            write_dat(self.outfile[:-4]+".dat",self.outfile)
            return True
        if not rendering(pattern=1):
            return False
        if not rendering(pattern=2):
            return False
        write_dat(self.outfile[:-4]+".dat",self.outfile)
        return True

class povray_template():
    def __init__(self,outfile):
        self.outfile=outfile
    def write_snow(self,out):
        snow_outfile=os.path.dirname(out)+"/snow.inc"
        with open(snow_outfile,mode="w") as f:
            f.write("#declare winter_light=\n")
            f.write("light_source {\n\t<0,173,0>\n\tcolor rgb 33\n\tparallel\n\tpoint_at<0,0,0>\n}\n")
        return
    def write_file(self,out):
        with open(out,mode="w") as f:
            f.write('#include "snow.inc"\n')
            f.write('#include "temp.inc"\n')
            f.write('// ---add include files---\n')
            f.write('\n')
            f.write('// -----------------------\n')
            f.write('// The default tile scale in this pov-ray file (not for pak file)\n')
            f.write('#local paksize=128;\n')
            f.write('\n')
            f.write('\n')
            f.write('// ---camera setting---\n')
            f.write('camera {\n')
            f.write('\torthographic\n')
            f.write('\tlocation <100,81.64965809277,100>*number_hight*paksize/128*10\n')
            f.write('\tlook_at <0,0.5,0>*paksize/128\n')
            f.write('\tright<1,0,-1> *paksize*number_width*2\n')
            f.write('\tup<1,0,1>  *paksize*number_hight/2*5\n')
            f.write('\t}\n')
            f.write('\n')
            f.write('\n')
            f.write('// ---light setting---\n')
            f.write('light_source {\n')
            f.write('\t<0,173,100>*100\n')
            f.write('\tcolor rgb 1\n')
            f.write('\tparallel\n')
            f.write('\tpoint_at<0,0,0>\n')
            f.write('}\n')
            f.write('// If winter==1, set a light to make the snow cover.\n')
            f.write('#if(winter)\n')
            f.write('\tlight_source{winter_light}\n')
            f.write('#end\n')
            f.write('\n')
            f.write('// ---background color #E7FFFF---\n')
            f.write('#declare bg_texture=\n')
            f.write('texture{\n')
            f.write('\tpigment{color rgb<0.9058823529411765,1,1>}\n')
            f.write('\tfinish{\n')
            f.write('\t\tdiffuse 0\n')
            f.write('\t\temission rgb<0.78,1,1>\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('\n')
            f.write('\n')
            f.write('// ----------------------------------\n')
            f.write('//\n')
            f.write('// the name of the object with all objects merged must be "obj"\n')
            f.write('//\n')
            f.write('// ---make objects below this line---\n')
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('// platform center\n')
            f.write('#declare obj_c=\n')
            f.write('\n')
            f.write('\n')
            f.write('// platform single\n')
            f.write('#declare obj_s=\n')
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('// platform front end\n')
            f.write('#declare obj_f=\n')
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('// platform back end\n')
            f.write('#declare obj_b=\n')
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('// platform wall (and background color for diagonal tiles)\n')
            f.write('#declare wall=\n')
            f.write('#if(make_front_image*diagonal_param > 0)\n')
            f.write('object{box{<0-.002,0,0-.002>,<paksize/2+.002,paksize/2,paksize/2+.002>}texture{bg_texture}}\n')
            f.write('#else\n')
            f.write('// please edit here!\n')
            f.write('object{}\n')
            f.write('#end\n')
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('// ---make objects above this line---\n')
            f.write('// \n')
            f.write('//\n')
            f.write('//\n')
            f.write('// ---put the obj---\n')
            f.write('#declare output_obj=\n')
            f.write('#if(diagonal_param=1)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_c\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,45,0>\n')
            f.write('\t\t\ttranslate<-paksize/4,0,paksize/4>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#elseif(diagonal_param=2)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_c\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,-45,0>\n')
            f.write('\t\t\ttranslate<paksize/2,0,0>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#else\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{obj_c}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#end\n')
            f.write('// ---output_area_set---\n')
            f.write('#declare output_area_set_x1=\n')
            f.write('#if((make_front_image-1)*(make_front_image-1)+diagonal_param*diagonal_param=0)\n')
            f.write('object{merge{box{<0-0.1,paksize/8,0-0.1>,<paksize*int_y/2+0.1,paksize*int_z,paksize*int_x/2+0.1>}box{<0-0.11,0+paksize/128,paksize*int_x/4>,<paksize*int_y/2+0.11,paksize*int_z,paksize*int_x/2+0.11>}}texture{bg_texture}}\n')
            f.write('#elseif((make_front_image-1)*(make_front_image-1)+(diagonal_param-1)*(diagonal_param-1)=0)\n')
            f.write('object{difference {\n')
            f.write('\tbox{<-paksize/2,0-.1,-paksize/2>,<paksize,paksize/2,paksize>}\n')
            f.write('\tobject{box{<-paksize*3*sqrt(2)/8,-paksize/2,-paksize*3*sqrt(2)/8>,<paksize*3*sqrt(2)/8,paksize/8+.120001,paksize*3*sqrt(2)/8>}rotate<0,45,0>}\n')
            f.write('}}\n')
            f.write('#else\n')
            f.write('object{box{<-paksize,-paksize*int_y,-paksize>,<paksize*(max(int_x,int_z)+2)/2+0.1,paksize*int_y,paksize*(max(int_x,int_z)+2)/2>}}\n')
            f.write('#end\n')
            f.write('#declare output_area_set_z1=\n')
            f.write('#if((make_front_image-1)*(make_front_image-1)+diagonal_param*diagonal_param=0)\n')
            f.write('object{merge{box{<-paksize,paksize/8,-paksize>,<paksize*(int_x+2)/2+0.1,paksize*int_z,paksize*(int_y+2)/2+0.1>}box{<paksize*int_x/4,0+paksize/128,0-0.11>,<paksize*int_x/2+0.11,paksize*int_z,paksize*int_y/2+0.11>}}texture{bg_texture}}\n')
            f.write('#elseif((make_front_image-1)*(make_front_image-1)+(diagonal_param-2)*(diagonal_param-2)=0)\n')
            f.write('object{difference {\n')
            f.write('\tbox{<-paksize/2,0-.1,-paksize/2>,<paksize,paksize/2,paksize>}\n')
            f.write('\tobject{box{<-paksize*3*sqrt(2)/8,-paksize*int_z,-paksize*3*sqrt(2)/8>,<paksize*3*sqrt(2)/8,paksize/8+.120001,paksize*3*sqrt(2)/8>}rotate<0,45,0>}\n')
            f.write('}}\n')
            f.write('#else\n')
            f.write('object{box{<-paksize,-paksize*int_z,-paksize>,<paksize*(max(int_x,int_z)+2)/2+0.1,paksize*int_z,paksize*(max(int_x,int_z)+2)/2>}}\n')
            f.write('#end\n')
            f.write('#declare output_area_set_x2=\n')
            f.write('#if((make_front_image-1)*(make_front_image-1)+diagonal_param*diagonal_param=0)\n')
            f.write('object{merge{box{<0-0.1,paksize/8,0-0.1>,<paksize*int_y/2+0.1,paksize*int_z,paksize*int_x/2+0.1>}box{<0-0.11,0+paksize/128,paksize*int_x/4>,<paksize*int_y/2+0.11,paksize*int_z,paksize*int_x/2+0.11>}}texture{bg_texture}}\n')
            f.write('#elseif((make_front_image-1)*(make_front_image-1)+(diagonal_param-1)*(diagonal_param-1)=0)\n')
            f.write('object{difference {\n')
            f.write('\tbox{<-paksize/2,0-.1,-paksize/2>,<paksize,paksize/2,paksize>}\n')
            f.write('\tobject{box{<-paksize*1*sqrt(2)/8,-paksize*int_z,-paksize*1*sqrt(2)/8>,<paksize*1*sqrt(2)/8,paksize/8+.120001,paksize*1*sqrt(2)/8>}rotate<0,45,0>}\n')
            f.write('}}\n')
            f.write('#else\n')
            f.write('object{box{<-paksize,-paksize*int_y,-paksize>,<paksize*(max(int_x,int_z)+2)/2+0.1,paksize*int_y,paksize*(max(int_x,int_z)+2)/2>}}\n')
            f.write('#end\n')
            f.write('#declare output_area_set_z2=\n')
            f.write('#if((make_front_image-1)*(make_front_image-1)+diagonal_param*diagonal_param=0)\n')
            f.write('object{merge{box{<-paksize,paksize/8,-paksize>,<paksize*(int_x+2)/2+0.1,paksize*int_z,paksize*(int_y+2)/2+0.1>}box{<paksize*int_x/4,0+paksize/128,0-0.11>,<paksize*int_x/2+0.11,paksize*int_z,paksize*int_y/2+0.11>}}texture{bg_texture}}\n')
            f.write('#elseif((make_front_image-1)*(make_front_image-1)+(diagonal_param-2)*(diagonal_param-2)=0)\n')
            f.write('object{difference {\n')
            f.write('\tbox{<-paksize/2,0-.1,-paksize/2>,<paksize,paksize/2,paksize>}\n')
            f.write('\tobject{box{<-paksize*1*sqrt(2)/8,-paksize*int_z,-paksize*1*sqrt(2)/8>,<paksize*1*sqrt(2)/8,paksize/8+.120001,paksize*1*sqrt(2)/8>}rotate<0,45,0>}\n')
            f.write('}}\n')
            f.write('#else\n')
            f.write('object{box{<-paksize,-paksize*int_z,-paksize>,<paksize*(max(int_x,int_z)+2)/2+0.1,paksize*int_z,paksize*(max(int_x,int_z)+2)/2>}}\n')
            f.write('#end\n')
            f.write('\n')
            f.write('// Place objects in 4 directions\n')
            f.write('object{merge{\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj}\n')
            f.write('\tobject{output_area_set_z1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*3/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,90,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_x1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*1/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,180,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_y/2\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_z2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-1)/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,270,0>\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_y/2}\n')
            f.write('\tobject{output_area_set_x2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-3)/4\n')
            f.write('\t}}\n')
            f.write('\tscale<1,.8165,1> // To set 1 distance of y direction as 1px, rescaling the hight\n')
            f.write('\ttranslate<-1,0,-1>*paksize*2\n')
            f.write('}\n')
            f.write('#declare output_obj=\n')
            f.write('#if(diagonal_param=1)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_b\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,45,0>\n')
            f.write('\t\t\ttranslate<0,0,paksize/2>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#elseif(diagonal_param=2)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_b\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,-45,0>\n')
            f.write('\t\t\ttranslate<paksize/4,0,paksize/4>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#else\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{obj_b}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#end\n')
            f.write('object{merge{\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj}\n')
            f.write('\tobject{output_area_set_z1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*3/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,90,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_x1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*1/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,180,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_y/2\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_z2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-1)/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,270,0>\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_y/2}\n')
            f.write('\tobject{output_area_set_x2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-3)/4\n')
            f.write('\t}}\n')
            f.write('\tscale<1,.8165,1> // To set 1 distance of y direction as 1px, rescaling the hight\n')
            f.write('\ttranslate<-1,0,-1>*paksize*1\n')
            f.write('}\n')
            f.write('#declare output_obj=\n')
            f.write('#if(diagonal_param=1)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_f\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,45,0>\n')
            f.write('\t\t\ttranslate<-paksize/2,0,0>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#elseif(diagonal_param=2)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_f\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,-45,0>\n')
            f.write('\t\t\ttranslate<paksize/2+paksize/4,0,-paksize/4>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#else\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{obj_f}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#end\n')
            f.write('object{merge{\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj}\n')
            f.write('\tobject{output_area_set_z1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*3/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,90,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_x1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*1/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,180,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_y/2\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_z2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-1)/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,270,0>\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_y/2}\n')
            f.write('\tobject{output_area_set_x2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-3)/4\n')
            f.write('\t}}\n')
            f.write('\tscale<1,.8165,1> // To set 1 distance of y direction as 1px, rescaling the hight\n')
            f.write('\ttranslate<-1,0,-1>*paksize*0\n')
            f.write('}\n')
            f.write('#declare output_obj=\n')
            f.write('#if(diagonal_param=1)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_s\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,45,0>\n')
            f.write('\t\t\ttranslate<-paksize/4,0,paksize/4>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#elseif(diagonal_param=2)\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{\n')
            f.write('\t\t\tobj_s\n')
            f.write('\t\t\tscale<1/sqrt(2),1,sqrt(2)>\n')
            f.write('\t\t\trotate<0,-45,0>\n')
            f.write('\t\t\ttranslate<paksize/2,0,0>\n')
            f.write('\t\t}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#else\n')
            f.write('object{\n')
            f.write('\tintersection{\n')
            f.write('\t\tobject{obj_s}\n')
            f.write('\t\tobject{wall}\n')
            f.write('\t}\n')
            f.write('}\n')
            f.write('#end\n')
            f.write('object{merge{\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj}\n')
            f.write('\tobject{output_area_set_z1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*3/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,90,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_x1}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*1/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,180,0>\n')
            f.write('\t\ttranslate<0,0,1>*paksize*int_y/2\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_x/2}\n')
            f.write('\tobject{output_area_set_z2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-1)/4\n')
            f.write('\t}\n')
            f.write('\tobject{\n')
            f.write('\tintersection{object{output_obj\n')
            f.write('\t\trotate<0,270,0>\n')
            f.write('\t\ttranslate<1,0,0>*paksize*int_y/2}\n')
            f.write('\tobject{output_area_set_x2}}\n')
            f.write('\t\ttranslate<-1,0,1>*paksize*number_width*(-3)/4\n')
            f.write('\t}}\n')
            f.write('\tscale<1,.8165,1> // To set 1 distance of y direction as 1px, rescaling the hight\n')
            f.write('\ttranslate<-1,0,-1>*paksize*(-1)\n')
            f.write('}\n')
        return
    def make_template(self):
        self.write_snow(self.outfile)
        print("make snow.inc")
        self.write_file(self.outfile)
        print("make "+self.outfile)
        print("make templates successfully")
        return