#!/bin/env python3

# Import required modules
from sys import argv
from markdown import markdown as md
# Manage system args
if len(argv)!=1:
    inpfile=argv[1]
else:
    inpfile="index.md"
# Get file content to work on
with open(inpfile.strip(),encoding="UTF-8") as file: content=file.read()
# Define variable parser
def parse_var(attr:str):
    attr=attr.strip().split(":")[1]
    # If value is a variable, convert it.
    if attr.startswith("(") and attr.endswith(")"):
        return f"var(--{attr[1:-1]})"
    else:
        return attr
# Define parser function
def parse_css(attrs):
    styles=""
    # Parse CSS
    for attr in attrs:
        attr=attr.strip()
        if   attr=="hcenter"               : styles+="            justify-content:center;\n"
        elif attr=="vcenter"               : styles+="            align-items:center;\n"
        elif attr=="txtcenter"             : styles+="            text-align:center !important;\n"
        elif attr=="bgtile"                : styles+="            background-size:unset;\n"
        elif attr=="bgmix"                 : styles+="            background-blend-mode:overlay;\n"
        elif attr.startswith("txtcol:")    : styles+="            color:"+parse_var(attr)+" !important;\n"
        elif attr.startswith("bgcol:")     : styles+="            background-color:"+parse_var(attr)+";\n"
        elif attr.startswith("bg:")        : styles+="            background-image:url(\""+parse_var(attr)+"\");\n"
        elif attr.startswith("rotate:")    : styles+="            transform:rotate("+parse_var(attr)+"deg);\n"
        elif attr.startswith("shadow:")    : styles+="            filter: drop-shadow(0 0 0.5vh "+parse_var(attr)+");\n"
        elif attr.startswith("txtshadow:") : styles+="            text-shadow:0 0 0.5vh "+parse_var(attr)+";\n"
    print(styles,attrs)
    return styles
# Split into parts to determine jobs
parts=content.split("\n^^^^\n")
settings=parts[0].split("\n")
content=parts[1].split("\n====\n")
# Default or empty variables
mode="normal"
doc_title="Slide Show"
presets={}
css={}
result=""
variables={}
additional_css=""
begin_js=""
final_js=""
# Process Slides
for sett in settings:
    # Document Name
    if   sett[:3]=="dn{" and sett[-1]=="}": doc_title=sett[3:-1]
    # Design
    elif mode=="normal":
        # Change modes
        if   sett.strip()[:3]=="ds{" : mode="design"
        elif sett.strip()[:3]=="vr{" : mode="variables"
        elif sett.strip()[:3]=="ps{" : mode="presets"
        elif sett.strip()[:4]=="css{": mode="css"
        elif sett.strip()[:4]=="bjs{": mode="begin_js"
        elif sett.strip()[:4]=="fjs{": mode="final_js"
    # Design mode, predefined tags
    elif mode=="design":
        # All Elements
        if   sett.strip()[:4]=="all{": css[".slide *"]            = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Title
        if   sett.strip()[:4]=="ttl{": css["slidetitle"]          = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Table
        elif sett.strip()[:4]=="tbl{": css["table"]               = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Image
        elif sett.strip()[:4]=="img{": css["img"]                 = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Paragraph
        elif sett.strip()[:4]=="prg{": css["p"]                   = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 1
        elif sett.strip()[:4]=="hd1{": css["h1"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 2
        elif sett.strip()[:4]=="hd2{": css["h2"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 3
        elif sett.strip()[:4]=="hd3{": css["h3"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 4
        elif sett.strip()[:4]=="hd4{": css["h4"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 5
        elif sett.strip()[:4]=="hd5{": css["h5"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Header 6
        elif sett.strip()[:4]=="hd6{": css["h6"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Table Header
        elif sett.strip()[:4]=="thd{": css["th"]                  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Table First Column
        elif sett.strip()[:4]=="tfc{": css["tr > td:first-child"] = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Table Odd Row
        elif sett.strip()[:4]=="tor{": css["tr:nth-child(odd)"]   = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Table Even Row
        elif sett.strip()[:4]=="ter{": css["tr:nth-child(even)"]  = parse_css(sett.split("{")[1].split("}")[0].split(","))
        # Turn back to normal mode
        elif sett=="}": mode="normal"
    # Variables mode
    elif mode=="variables":
        # Turn back to normal mode
        if sett=="}":
            mode="normal"
        # Set Variables
        else:
            keyval=sett.strip().split(":")
            variables[keyval[0]]=keyval[1]
    # Presets mode
    elif mode=="presets":
        # Turn back to normal mode
        if sett=="}":
            mode="normal"
        else:
            namestyles=sett.strip().split("{")
            presets[namestyles[0]]=namestyles[1][:-1]
    elif mode=="css":
        if sett=="}":
            mode="normal"
        else:
            additional_css+=("        " if sett.startswith("    ") else "      " if sett.startswith("    ") else "      ")+sett+"\n"
    elif mode=="begin_js":
        if sett=="}":
            mode="normal"
        else:
            begin_js+=sett+"\n"
    elif mode=="final_js":
        if sett=="}":
            mode="normal"
        else:
            final_js+=sett+"\n"
    else:
        print(sett)
# Parse variables
css[":root"]=""
for var in variables:
    css[":root"]+=f"            --{var}:{variables[var]};\n"
# Parse presets
for preset in presets:
    attrs=set(presets[preset].split(","))
    css["."+preset]=parse_css(attrs)
# Open file to work on
with open("".join(inpfile.split(".")[:-1])+".html",mode="w",encoding="UTF-8") as res_file:
    # Create result file content and place required tags
    result="""<!DOCTYPE html>
<!-- This document automatically generated with SlideMaker Developed By Elagoht. -->
<!-- Visit Elagoht's GitHub page: https://github.com/Elagoht -->
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/design.css">
        <title>{__title}</title>
    </head>
    <style>
{__css}    </style>
    <script id="begin_js">
{__bjs}    </script>
    <body>
        <header id="slide_info">{__title}</header>
        <section>
"""
    # Process slides one by one
    for index,slide in enumerate(content):
        # Create a new slide tag
        result+="            <div class=\"slide\">\n"
        # Get lines converted to markdown
        for line in md(slide,extensions=["tables","attr_list","fenced_code","nl2br","sane_lists"]).split("\n"):
            line=line.strip()
            # If slide design defined process styles
            if "sd{" in line and "}" in line:
                # Get list of styles
                attrs=set((line.split("{")[1].split("}")[0].split(",")))
                # Create a css style for that slide
                css[f".slide:nth-child({str(index+1)})"]=parse_css(attrs)
            # Add preset class to current slide
            elif line.startswith("<p>ps{") or line.startswith("ps{"):
                preset_name=line.split("{")[1].split("}")[0]
                line_breaks=result.split("\n")
                line_breaks.reverse()
                for index,line_break in enumerate(line_breaks):
                    if "<div class=\"" in line_break and "slide\">" in line_break:
                        break
                line_breaks[index]=line_breaks[index].replace("\"",f"\"{preset_name} ",1)
                line_breaks.reverse()
                result="\n".join(line_breaks)
            # Set slide title header
            elif line.startswith("<p>\\"):
                line=line.replace("<p>\\","<slidetitle>").replace("</p>","</slidetitle>")
                result+=f"                {line}\n"
            # Finally add markdown data
            else:
                result+=f"                {line}\n"
        result+="            </div>\n"
    # Define some JavaScript variables
    begin_js+=f"  const page_count={index+1}\n"
    # Add bottom of HTML
    result+="""        </section>
        <div id="transition-con">
            <div id="transition"></div>
        </div>
        <footer>
            <div>
                <nav id="controls">
                    <div id="first" onclick="slide_first()">&#8612;</div>
                    <div id="previous" onclick="slide_prev()">&#8656;</div>
                    <div>
                        <input id="slide-number" type="number" value="1" min="1" required>
                        <span id="slide-count"></span>
                    </div>
                    <div id="next" onclick="slide_next()">&#8658;</div>
                    <div id="last" onclick="slide_last()">&#8614;</div>
                </nav>
            </div>
        </footer>
    </body>
    <script src="/behaviour.js"></script>
    <script id="final_js">
{__fjs}    </script>
</html>"""
    # Remove paragraph element around images
    result=result.replace("<p><img","<img").replace("\"></p>","\">")
    # Add support for links to slides
    result=result.replace("[++]","</goto>")
    result=result.replace("[+","<goto onclick=\"go_to(").replace("+]",");\">")
    # Add additional CSS defined by user
    css="".join("        "+key+" {\n"+style+"        }\n" for key,style in zip(css.keys(),css.values()))
    css+=additional_css
    # Add created css to html and write document name
    result=result.format(__title=doc_title,__css=css,__bjs=begin_js,__fjs=final_js)
    # Write content to output file
    res_file.write(result)
