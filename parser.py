#!/bin/env python3

# TODO make presets

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
        if   attr=="hcenter"            : styles+="            justify-content:center;\n"
        elif attr=="vcenter"            : styles+="            align-items:center;\n"
        elif attr=="txtcenter"          : styles+="            text-align:center !important;\n"
        elif attr=="bgtile"             : styles+="            background-size:unset;\n"
        elif attr=="bgmix"              : styles+="            background-blend-mode:overlay;\n"
        elif attr.startswith("txtcol:") : styles+="            color:"+parse_var(attr)+" !important;\n"
        elif attr.startswith("bgcol:")  : styles+="            background-color:"+parse_var(attr)+";\n"
        elif attr.startswith("bg:")     : styles+="            background-image:url(\""+parse_var(attr)+"\");\n"
    return styles
# Split into parts to determine jobs
parts=content.split("\n^^^^\n")
settings=parts[0].split("\n")
content=parts[1].split("\n====\n")
# Default or empty variables
print(settings)
mode="normal"
doc_title="Slide Show"
presets={}
designs={}
css={}
result=""
variables={}
# Process Slides
for sett in settings:
    # Document Name
    if   sett[:3]=="dn{" and sett[-1]=="}": doc_title=sett[3:-1]
    # Design
    elif mode=="normal":
        # Change modes
        if   sett.strip()[:3]=="ds{": mode="design"
        elif sett.strip()[:3]=="vr{": mode="variables"
        elif sett.strip()[:3]=="ps{": mode="presets"
    # Preset mode
    elif mode=="design":
        # Title
        if   sett.strip()[:4]=="ttl{": designs[".title"]=sett[4:-1]
        # Table
        elif sett.strip()[:4]=="tbl{": designs["table"]=sett[4:-1]
        # Image
        elif sett.strip()[:4]=="img{": designs["img"]=sett[4:-1]
        # Paragraph
        elif sett.strip()[:4]=="prg{": designs["p"]=sett[4:-1]
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
            presets[namestyles[0]]=namestyles[1]
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
            elif line.startswith("<p>ps{") and line.endswith("}</p>"):
                preset_name=line[6:-5]
                line_breaks=result.split("\n")
                line_breaks.reverse()
                for index,line_break in enumerate(line_breaks):
                    if "<div class=\"slide" in line_break:
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
</html>"""
    # Remove paragraph element around images
    result=result.replace("<p><img","<img").replace("\"></p>","\">")
    # Add support for links to slides
    result=result.replace("[++]","</goto>")
    result=result.replace("[+","<goto onclick=\"go_to(").replace("+]",");\">")
    # Add created css to html and write document name
    result=result.format(__title=doc_title,__css="".join("        "+key+" {\n"+style+"        }\n" for key,style in zip(css.keys(),css.values())))
    # Write content to output file
    res_file.write(result)
