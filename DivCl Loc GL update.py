from pathlib import Path
import os

# Set directory and filename for macro here - will be created if it does not exist already
dir = Path.home() / 'Documents' / 'Macros'
f_name = 'DivCl Location GL Posting'
f_ext = '.mac'


# FUNCTIONS:
def ScreenClear():
    os.system('cls' if os.name == 'nt' else 'clear')

def RangeArray(startAt, endAt, terrYN : bool):
    # Fills an array of strings from a set (numerical) starting point and end point
    arr = list(range(startAt, endAt + 1))
    if terrYN == True:
        for i in range(len(arr)):
            arr[i] = str(arr[i]).rjust(3, '0')
    else:
        for i in range(len(arr)):
            arr[i] = str(arr[i])
    return arr

def get_div():
    while True:
        confirmYN = ''
        try:
            div_no = input('Enter the division # you want to work with: ').strip()
            if not div_no.isnumeric():
                print("Division # must be numeric only.")
                continue
            elif len(div_no) < 1:
                print("Sorry, I didn't understand that.")
                continue
            elif len(div_no) > 4:
                print("Division # cannot be more than 4 digits.")
            else:
                try:
                    confirmYN = input('Use divison # ' + div_no + '? (Y/N/Exit): ').upper().strip()
                    if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                        print("Sorry, I didn't understand that.")
                        continue
                    elif confirmYN == 'EXIT':
                        raise SystemExit(0)
                    elif confirmYN in {'N', 'NO'}:
                        continue
                    else:
                        break
                except ValueError:
                    print("Sorry, I didn't understand that.")
                    continue
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
    
    return div_no

def get_loc_arr(new_old):
    done = False
    while not done:
        invalid = False
        counter = 0

        t_txt = '''Enter {sub_} locations you wish to work with (up to ~20, client won't run the macro if the file is too big).
Enter individual store #s separated by commas, AND/OR enter ranges of store #s with a dash in the middle.
Example: 009, 011-013, 022
MUST use commas to separate each store or range of stores.
(shortcut: type ALL to use 001-225.)
Type EXIT to quit.
'''.format(sub_=new_old)

        t_input = input(t_txt).strip().upper()
        if t_input == 'EXIT':
            raise SystemExit(0)
        # shortcut - all stores 001-225
        elif t_input == 'ALL':
            # confirm
            yn = input("Use range 001-225? [Y/N]: ").strip().upper()
            if yn in {"Y", "YES"}:
                t_input = "001-225"
                t_arr = RangeArray(1, 225, True)
                done = True
                break
            else:
                invalid = True
                continue

        elif t_input == '':
            continue
        else:
            # Validate
            charcnt = 0
            for char in t_input:
                charcnt+=1
                if counter > 3:
                    print("It looks like you entered a territory/store number that was more than 3 digits. Please check your territory/store numbers and make sure to separate each one with a comma.")
                    invalid = True
                    break

                if char not in {',','-',' '} and char.isnumeric == False:
                    print("Invalid character, only numbers, commas and dashes are accepted.")
                    invalid = True
                    break
                elif char in {',','-'}:
                    # Reset counter to 0
                    counter = 0
                    continue
                elif charcnt == len(t_input):
                    # Check length of previous 'word'
                    counter+=1
                    if counter > 3:
                        print("It looks like you entered a territory/store number that was more than 3 digits. Please check your territory/store numbers and make sure to separate each one with a comma.")
                        invalid = True
                        break
                elif char != ' ':
                    # Count characters omitting spaces or commas
                    counter+=1
            

            if invalid == False:
                # Remove all spaces
                t_input = t_input.replace(" ", "")
                # Split on commas and send to array
                t_arr = t_input.split(',')
                # Look for ranges
                for element in t_arr:
                    x = element.find('-')
                    if x != -1:
                        start_rng = int(element[0:x])
                        end_rng = int(element[(x+1):])
                        temp_arr = RangeArray(start_rng, end_rng, True)
                        for x in temp_arr:
                            t_arr.append(x)
                        t_arr.remove(element)
                
                # Bug fix: delete first value if blank
                if t_arr[0] == '':
                    del t_arr[0]
                # Format all values as ###
                for i in range(len(t_arr)):
                    t_arr[i] = str(t_arr[i]).rjust(3, '0')
                
                # Remove duplicates and sort
                t_arr = list(set(t_arr))
                t_arr.sort()

                # Confirm with user
                conf_str = ''
                for element in t_arr:
                    conf_str += element + ', '
                conf_str = conf_str[:-2] #removes last comma-space
                while True:
                    confirmYN = input('Confirm Locations to use:\n' + conf_str + '\n[Y/N/Exit]: ').strip().upper()
                    if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                        print("Sorry, I didn't understand that.")
                        continue
                    elif confirmYN == 'EXIT':
                        raise SystemExit(0)
                    elif confirmYN in {'Y', 'YES'}:
                        done = True
                        break
                    else:
                        break

    return t_arr

def macro_text_function(new_old, t_arr):
    # First, header and initial navigation:
    if new_old == 'EXISTING':
        repl_text = 'Edit EXISTING'
    else:
        repl_text = 'Create NEW'

    start_text = '''Description = {var} GL values for a given div/class/location
REM From loc: {minloc}
REM To loc: {maxloc}
REM initial navigation to Location G/L Posting Search
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[pf12]
[wait inp inh]

"1
[enter]
"101
[enter]
"219
[enter]
"305
[enter]
[wait inp inh]

[backtab]
REM start loop here
'''.format(var=repl_text, minloc=t_arr[0], maxloc=t_arr[-1])

    # Next, assign the looping part to a new variable, then append to m_txt
    # Values will be substituted in using a dictionary 'dict'.
    for loc in t_arr:
        temp_loc = int(loc) # convert to int to lose leading zeroes...
        gl_loc = str(temp_loc) + '00' # then convert back to string and add 2 zeroes at end

        dict = { 'loc' : loc, 'gl_loc' : gl_loc, 'div' : div_no, 'class' : inv_cls, 'cl_desc' : inv_cls_desc }

        # The following will differ depending on whether new_old == 'NEW' or 'EXISTING'
        if new_old == 'NEW':
            add_text = '''REM *location here*
"{loc}
[field+]
[wait inp inh]

"{div}
[field+]
[enter]
[wait app]
[wait inp inh]


[pf1]
[wait app]
[wait inp inh]

"{class}
[field+]



"{cl_desc}
[wait app]
[wait inp inh]
REM [pause]
REM The following is to handle descriptions of variable length
REM - should always get cursor to the right place
[up]
[up]
[up]
[up]
REM [pause]
[wait app]
[wait inp inh]
[tab field]
[tab field]
[tab field]
[tab field]
REM [pause]
[wait app]
[wait inp inh]
REM **** Location GL number
"{gl_loc}
[field+]
"4000
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"5000
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[wait app]
[wait inp inh]
REM [pause]

[pf22]
[wait app]
[wait inp inh]
REM **** Location GL number
"{gl_loc}
[field+]
"1200.0000
[field+]

[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]

[up]
[up]
REM cursor is now in Location field - ready for next location

'''

        elif new_old == 'EXISTING':
            add_text = '''REM *location here*
"{loc}
[field+]
[wait inp inh]

"{div}
[field+]
[wait app]
[wait inp inh]


"{class}
[wait app]
[wait inp inh]
[field+]
[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]
REM [pause]
[down]
[down]
REM [pause]

[pf5]
[wait app]
[wait inp inh]


"{cl_desc}
[wait app]
[wait inp inh]
REM [pause]
REM The following is to handle descriptions of variable length
REM - should always get cursor to the right place
[up]
[up]
REM [pause]
[wait app]
[wait inp inh]
[tab field]
[tab field]
[tab field]
REM [pause]
[wait app]
[wait inp inh]
REM **** Location GL number
"{gl_loc}
[field+]
"4000
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"5000
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
REM **** Location GL number
"{gl_loc}
[field+]
"1200
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[field+]
[field+]
"999999
[field+]
[wait app]
[wait inp inh]
REM [pause]

[pf22]
[wait app]
[wait inp inh]
REM **** Location GL number
"{gl_loc}
[field+]
"1200.0000
[field+]

[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]
[enter]
[wait app]
[wait inp inh]

[tab field]
[tab field]
REM cursor is now in Location field - ready for next location

'''
    


        # Format to insert variables from dictionary
        add_text = add_text.format(**dict)

        # Append to start_text
        start_text += add_text

    return start_text

def macro_export_function(m_text, dir, f_name, f_ext, new_old, class_no, rng=''):
    # Add NEW or EXISTING to filename followed by f_ext
    f_name += ' - ' + new_old + ' ' + class_no
    if range != '':
        f_name += ' ' + rng + f_ext
    else:
        f_name += f_ext

    # Write finalized m_txt string to file
    Path(dir / f_name).write_text(m_text)

# End FUNCTIONS


# PUBLIC VARIABLE for class descriptions in division 27
Div_27_Arr = [['2700','DM Heavy Duty Storage Cabinets'], ['2701','DM Louvered Panel Systems'], ['2702','DM Rotabins Revolving Shelves'], ['2703','DM Safety Storage'], ['2704','DM Carts and Trucks'], ['2705','DM Workbenches Workstations'], ['2706','DM Specialty Storage'], ['2707','DM Jobsite Storage'], ['2708', 'DM Accessories']]


# MAIN SECTION
# Check if new or existing
print('''Is this for a NEW Location G/L Posting, or an EXISTING one?
You can check by going into A/R->File Maintenance->Misc->Location G/L Posting. Type in the location, division, and class, and see if there is already an editable entry.

This is *important* as you cannot add a new posting when one already exists. The macro will fail and may enter random data.''')
while True:
    try:
        new_old = input("\nType NEW or EXISTING (or EXIT to quit) and press Enter:\n\n").strip().upper()

        if new_old not in {'NEW', 'EXISTING', 'EXIT'}:
            print("Sorry, I didn't understand that.")
            continue
        elif new_old == 'EXIT':
            raise SystemExit(0)
        else:
            break
    except ValueError:
        print("Sorry, I didn't understand that.")
        continue


ScreenClear()
# Get inv class number (only one at a time, since this will loop through every territory)
while True:
    confirmYN = ''
    try:
        inv_cls = input('Enter the inventory class # you want to work with: ').strip()
        if not inv_cls.isnumeric():
            print("Class # must be numeric only.")
            continue
        elif len(inv_cls) not in { 3, 4 }:
            print("Class # must be 3 or 4 digits.")
            continue
        else:
            try:
                confirmYN = input('Use inventory class # ' + inv_cls + '? (Y/N/Exit): ').upper().strip()
                if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                    print("Sorry, I didn't understand that.")
                    continue
                elif confirmYN == 'EXIT':
                    raise SystemExit(0)
                elif confirmYN in {'N', 'NO'}:
                    continue
                else:
                    break
            except ValueError:
                print("Sorry, I didn't understand that.")
                continue
    except ValueError:
        print("Sorry, I didn't understand that.")
        continue

ScreenClear()

# Get div # from first 1 or 2 digits of class - user will confirm later
div_no = inv_cls[:(len(inv_cls)-2)]


# Get class description
inv_cls_desc = ''
if str(div_no) == '27':
    for x in Div_27_Arr:
        if x[0] == str(inv_cls):
            inv_cls_desc = x[1]

if inv_cls_desc != '':
    while True:
        try:
            ScreenClear()
            confirmALL = input('Does this look correct?\n\nNew/Existing: ' + new_old + '\nDivision #: ' + div_no + '\nInventory class #: ' + inv_cls + '\nClass description: ' + inv_cls_desc + '\n\n[Y: Proceed]\n[N/E: Edit NEW/EXISTING]\n[DIV: Edit division #]\n[CLASS: Edit inventory class #]\n[DESC: Edit class description]\n[EXIT: Quit]\n\n').upper().strip()
            if confirmALL not in {'Y','YES','N/E', 'DIV', 'CLASS', 'DESC', 'EXIT'}:
                print("Sorry, I didn't understand that.")
                continue
            elif confirmALL == 'EXIT':
                raise SystemExit(0)
            elif confirmALL in {'Y', 'YES'}:
                break
            elif confirmALL == 'N/E':
                child_loop = True
                while child_loop == True:
                    confirmYN = ''
                    try:
                        new_old = input("\nType NEW or EXISTING (or EXIT to quit) and press Enter:\n").strip().upper()

                        if new_old not in {'NEW', 'EXISTING', 'EXIT'}:
                            print("Sorry, I didn't understand that.")
                            continue
                        elif new_old == 'EXIT':
                            raise SystemExit(0)
                        else:
                            child_loop = False
                            break
                    except ValueError:
                        print("Sorry, I didn't understand that.")
                        continue
                continue

            elif confirmALL == 'DIV':
                child_loop = True
                while child_loop == True:
                    confirmYN = ''
                    try:
                        div_no = input('Enter the division # you want to work with: ').strip()
                        if not div_no.isnumeric():
                            print("Division # must be numeric only.")
                            continue
                        elif len(div_no) not in { 1, 2, 4 }:
                            print("Invalid division #.")
                            continue
                        else:
                            try:
                                if len(div_no) == 4:
                                    print("WARNING: You entered division # " + div_no + ". Most DIVISION numbers are 2 digits. Please double-check that you have the correct number.")
                                confirmYN = input('Use division # ' + div_no + '? (Y/N/Exit): ').upper().strip()
                                if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                                    print("Sorry, I didn't understand that.")
                                    continue
                                elif confirmYN == 'EXIT':
                                    raise SystemExit(0)
                                elif confirmYN in {'N', 'NO'}:
                                    continue
                                else:
                                    child_loop = False
                                    break
                            except ValueError:
                                print("Sorry, I didn't understand that.")
                                continue
                    except ValueError:
                        print("Sorry, I didn't understand that.")
                        continue
                continue

            elif confirmALL == 'CLASS':
                child_loop = True
                while child_loop == True:
                    confirmYN = ''
                    try:
                        inv_cls = input('Enter the inventory class # you want to work with: ').strip()
                        if not inv_cls.isnumeric():
                            print("Class # must be numeric only.")
                            continue
                        elif len(inv_cls) not in { 3, 4 }:
                            print("Class # must be 3 or 4 digits.")
                            continue
                        else:
                            try:
                                confirmYN = input('Use inventory class # ' + inv_cls + '? (Y/N/Exit): ').upper().strip()
                                if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                                    print("Sorry, I didn't understand that.")
                                    continue
                                elif confirmYN == 'EXIT':
                                    raise SystemExit(0)
                                elif confirmYN in {'N', 'NO'}:
                                    continue
                                else:
                                    child_loop = False
                                    break
                            except ValueError:
                                print("Sorry, I didn't understand that.")
                                continue
                    except ValueError:
                        print("Sorry, I didn't understand that.")
                        continue
            
            elif confirmALL == 'DESC':
                child_loop = True
                while child_loop == True:
                    confirmYN = ''            
                    try:
                        inv_cls_desc = input('Enter the description for inventory class # ' + inv_cls + ' (case sensitive): ').strip()
                        if len(inv_cls_desc) > 30:
                            print("Class description must be 30 characters or fewer.")
                            continue
                        elif len(inv_cls_desc) < 1:
                            print("Sorry, I didn't understand that.")
                            continue
                        else:
                            try:
                                confirmYN = input('Does this look correct?\nNew/Existing: ' + new_old + '\nDivision #: ' + div_no + '\nInventory class #: ' + inv_cls + '\nClass description: ' + inv_cls_desc + '\n(Y/N/Exit): ').upper().strip()
                                if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                                    print("Sorry, I didn't understand that.")
                                    continue
                                elif confirmYN == 'EXIT':
                                    raise SystemExit(0)
                                elif confirmYN in {'N', 'NO'}:
                                    continue
                                else:
                                    child_loop = False
                                    break
                            except ValueError:
                                print("Sorry, I didn't understand that.")
                                continue
                    except ValueError:
                        print("Sorry, I didn't understand that.")
                        continue

            else:
                print("Oops! I don't know how you got here. Check the script!")
                os.system('pause')
                SystemExit(0)
                
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        
ScreenClear()

if inv_cls_desc == '':
    while True:
        confirmYN = ''            
        try:
            inv_cls_desc = input('Enter the description for inventory class # ' + inv_cls + ' (case sensitive): ').strip()
            if len(inv_cls_desc) > 30:
                print("Class description must be 30 characters or fewer.")
                continue
            elif len(inv_cls_desc) < 1:
                print("Sorry, I didn't understand that.")
                continue
            else:
                try:
                    confirmYN = input('Does this look correct?\nNew/Existing: ' + new_old + '\nDivision #: ' + div_no + '\nInventory class #: ' + inv_cls + '\nClass description: ' + inv_cls_desc + '\n(Y/N/Exit): ').upper().strip()
                    if confirmYN not in {'Y','N', 'YES', 'NO', 'EXIT'}:
                        print("Sorry, I didn't understand that.")
                        continue
                    elif confirmYN == 'EXIT':
                        raise SystemExit(0)
                    elif confirmYN in {'N', 'NO'}:
                        continue
                    else:
                        break
                except ValueError:
                    print("Sorry, I didn't understand that.")
                    continue
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue

ScreenClear()
# Get list of territories/locations to include.
t_arr = get_loc_arr(new_old)
        

ScreenClear()
# All variables acquired... time to generate the macro.
# Macro commands will be assigned to the variable m_text.
# Once finished, m_text will be written to the specified file.

# special case: all locations - break out into files w/ 20 locations each
if t_arr[0] == '001' and t_arr[-1] == '225':
    last_x = int(t_arr[-1]/20)
    for x in range(0, last_x + 1):
        start_x = (x * 20) + 1
        if x < last_x:
            end_x = start_x + 19
        else:
            end_x = last_x
        x_arr = RangeArray(start_x, end_x, True)
        x_text = macro_text_function(new_old, x_arr)
        x_rng = str(x_arr[0]) + '-' + str(x_arr[-1])
        macro_export_function(x_text, dir, f_name, f_ext, new_old, inv_cls, x_rng)
    print("Exports completed, exiting script.")
    os.system('pause')

else:
    m_text = macro_text_function(new_old, t_arr)

    # Export to file
    rng = str(t_arr[0]) + '-' + str(t_arr[-1])
    macro_export_function(m_text, dir, f_name, f_ext, new_old, inv_cls, rng)

    print("\nMacro file created.")
    while True:
        do_again = input("Do you want to re-run with additional locations? (Client can only handle about 20-25 in each macro file.) [Y/N]: ").strip().upper()
        if do_again not in {'Y', 'N', 'YES', 'NO'}:
            print("Sorry, I didn't understand that.")
            continue
        elif do_again in {'Y', 'YES'}:
            t_arr = get_loc_arr(new_old)
            m_text = macro_text_function(new_old, t_arr)
            rng = str(t_arr[0]) + '-' + str(t_arr[-1])
            macro_export_function(m_text, dir, f_name, f_ext, new_old, inv_cls, rng)
            print('Macro file created.')
            continue
        else:
            print('Exiting script')
            os.system('pause')
            break