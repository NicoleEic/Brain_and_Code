function minesearcher(varargin)
% ** function minesearcher(varargin)
% Main function of the minesearcher game
% by Nicole Eichert and Maximilian Cierpka. 
%
% The function can be called without input arguments to start with 
% the default settings for the intermediate level. If 3 optional
% arguments are entered, the first two correspond to the size of 
% the board, namely the number of rows and the number of columns, while 
% the third corresponds to the number of mines hidden in the field.
% The rules of the game can be accessed by opening the 'Help'-menue 
% in the game window.
%
% To access the help regarding the various local functions type:
% minesearcher>localfunction.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% varargin    cell-array  optional input argumens for game settings
% varargin{1} double      number of rows (mRows)
% varargin{2} double      number of columns (nCols)
% varargin{3} double      number of mines (nMines)
%
% <<< NO OUTPUT VARIABLES <<<



% ----------- Initialize default values for intermediate level ------------

% Number of rows.
mRows = 16;
% Number of columns.
nCols = 16;
% Number of mines.
nMines = 40;
% Edge length of the buttons.
btSize = 20;  

% Close any figures that might be opened before starting the game.
close all


% --------------- Deal with optional input arguments ----------------------

% If 3 optional input arguments are entered, take these as level-settings.
switch nargin
    case 3
        try
        % Check if the inputs are valid numbers and fit to the rules. The
        % initialized settings will then be overwritten.
        [mRows, nCols, nMines] = checkfieldconfig(varargin{1}, ...
                                                  varargin{2}, ...
                                                  varargin{3});
        catch
            % If an error occurs in the function checkfieldconfig, the
            % game starts with the initialized values.
            warn = warndlg(sprintf(['Invalid field configuration entered!\n' ...
                                    'The game is started with the default values.']), ...
                                    'Invalid input', 'modal');
            uiwait(warn);
        end
    case 0
        % Continue with initialized values.
    otherwise
        % If an unappropriate number of input values is given, the game
        % starts in the default mode.
        warn = warndlg(sprintf(['Wrong number of input values!\n' ...
                                'The game is started with the default values.']), ...
                                'Invalid input', 'modal');
        uiwait(warn);
end

% ----------------- Position and Size of game window ----------------------

% Some space is added as a border around the edge of the group of buttons
% (+12 pixels on each side) and on top for the smiley button, the counter 
% and the timer-display (+30 pixels).
figWidth = btSize*nCols+24;
figHeight = btSize*mRows+66;

% Get the screensize in order to position the game window.
screenSize = get(0, 'ScreenSize');
% Set the bottom-left corner of the game window.
xpos = ceil((screenSize(3)-figWidth)/2);
ypos = ceil((screenSize(4)-figHeight)/2);

% Generate the figure of the game window.
fig = figure('name', 'Minesearcher', ...
             'NumberTitle', 'off', ...
             'Position', [xpos, ypos, figWidth, figHeight], ...
             'MenuBar', 'None', ...
             'WindowButtonDownFcn', @setsmileyo, ...
             'WindowButtonUpFcn', @setsmileyface, ....  
             'CloseRequestFcn', @exitfcn);
         
% Move the game window to the center of the screen.     
movegui(gcf, 'center'); 
         
         
% -------------------------- Smiley button --------------------------------

% Load and resize smiley button.
imgSmiley = imresize(imread('Smiley.jpg'), [30, 30]);
% Generate smiley-button.
uiSmiley = uicontrol(fig, 'CData', imgSmiley, ...
                          'Position', [figWidth/2-15 figHeight-40 30 30], ...
                          'Callback', {@callbacknewgame, mRows, nCols, nMines}, ...
                          'Tag', 'smiley');                     
                      
% -------------------------- Mine counter ---------------------------------

% The variable "count" stores the number of hidden mines that 
% is displayed by the counter in the upper-left corner. 
count = sprintf('%03i', nMines);
% Generate display for the counter. The display is formatted
% so that 3 digits with leading zeros are shown.
uiCounter = uicontrol(fig, 'Style', 'text', ...
                           'Position', [12 figHeight-40 50 30], ...
                           'BackgroundColor', 'black', ...
                           'ForegroundColor', 'red', 'FontSize', 20, ...
                           'FontName', 'OCR A Extended', ...
                           'String', count, ...
                           'Tag', 'counter');

% -------------------------- Timer ----------------------------------------                     

% Generate the uiControl (display) for the timer.
uiTimer = uicontrol(fig, 'Style', 'text', ...
                         'Position', [figWidth-62 figHeight-40 50 30], ...
                         'BackgroundColor', 'black', ...
                         'ForegroundColor', 'red', ...
                         'FontSize', 20, ...
                         'FontName', 'OCR A Extended', ...
                         'String', '000', ...
                         'Tag', 'uiTimer');
                     
% Generate the timer and set timer properties.    
% The timer stops to update the timer-display when 999 seconds (16min 39s)
%  have been reached.
tm = timer('name', 'tm', ...
           'ExecutionMode', 'FixedRate', ...
           'TasksToExecute', 1000, ...
           'StartFcn', @timerstart, ...
           'TimerFcn', @timerupdater);
       
% The timer has to be stopped before a restart of the timer is possible.
% If the game restarts, an already running timer cannot be started again.
stop(tm);
start(tm);
       

% ------------------ 'Game'-menu, submenues and 'Help'-menu ---------------

uiMenu = uimenu(fig, 'Label', 'Game');
% Start a new game on the same difficulty with the previous settings.
subMenu(1) = uimenu(uiMenu, 'Label', 'New Game', ...
                            'Callback', {@callbacknewgame, mRows, nCols, nMines});
% Start a new game on difficulty 'Beginner'.                        
subMenu(2) = uimenu(uiMenu, 'Label', 'Beginner', ...
                            'Callback', {@callbacknewgame, 8, 8, 10});
% Start a new game on difficulty 'Intermediate'.                                                
subMenu(3) = uimenu(uiMenu, 'Label', 'Intermediate', ...
                            'Callback', {@callbacknewgame, 16, 16, 40});
% Start a new game on difficulty 'Expert'.                                                
subMenu(4) = uimenu(uiMenu, 'Label', 'Expert', ...
                            'Callback', {@callbacknewgame, 16, 30, 99});
% Start a new game with costumized settings.                                                
subMenu(5) = uimenu(uiMenu, 'Label', 'Custom...', ...
                            'Callback', @callbackcustom);
% Exit the game.                        
subMenu(6) = uimenu(uiMenu, 'Label', 'Exit', ...
                            'Callback', @exitfcn);

% The helptext is loaded from the file 'helptext.txt.'.
uiHelp = uimenu(fig, 'Label', 'Help', ...
                     'Callback', 'helpdlg(fileread(''helptext.txt''))');

                 
% -------------------- Minefield and field of numbers ---------------------           

% Generate underlying array with zeros and ones as minefield, where
% a one represents a hidden mine.
arr = [ones(1, nMines) zeros(1, mRows*nCols-nMines)];
% Form the game field and randomize the array to distribute the hidden mines.
arr = reshape(arr(randperm(length(arr))), mRows, nCols);

% Calculate the array of numbers of neighboring mines that will be later
% displayed on the uncovered fields.
numberArr = conv2(double(arr), [1 1 1; 1 0 1; 1 1 1], 'same');

% Store some variables in gcf to make them accessible for following
% subfunctions.
setappdata(gcf, 'mineField', arr);
setappdata(gcf, 'numberField', numberArr);
setappdata(gcf, 'level', [mRows, nCols, nMines]);
setappdata(gcf, 'toUncover', mRows*nCols-nMines);


% -------------------------- Set of fields --------------------------------

% Generate a set of fields that are stored in a cell array.

% Preallocate cell-array.
fields = cell(mRows, nCols); 

for j = 1:nCols % Fill rows.
   for i = 1:mRows % Fill columns.
    fields(i, j) = {uicontrol('Style', 'pushbutton', ...
                              'Position', [12+(j-1)*btSize ...       % Left.
                                           figHeight-50-i*btSize ... % Bottom.
                                           btSize ...                % Width.
                                           btSize], ...              % Height.
                              'BackgroundColor', [.7 .7 .7], ...
                              'Callback', @leftclick, ...
                              'ButtonDownFcn', @raiseflag, ...
                              'UserData', [i, j], ...
                              'Tag', 'field')};
    % The 2d-index of the field is stored in the property 'UserData'.
    % The appdata 'Mine' carries information about a hidden mine.    
    setappdata(fields{i, j}, 'Mine', arr(i, j));
  
   end
end


%% ------------------- Local functions called by clicks -------------------

% ----------------- Local functions regarding left clicks ----------------

function leftclick(src, eventdata)
% ** function leftclick(src, eventdata)
% This local function comprises the actions that are performed when  
% the user clicks on a field. It determines whether a mine is hit 
% and what number will be displayed on the field. 
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<


% Switch loop: Did the user hit a mine or not?
mine = getappdata(src, 'Mine');
switch mine

% -------------------- The user did not hit a mine. --------------------
    case 0
        
        % Read out the 2d-index of the field stored in the property 'UserData'.
        idx = get(src, 'UserData');
        a = idx(1);
        b = idx(2);
        % Uncover the field that has been clicked on.
        sumMines = uncover(a, b);
        if sumMines ~= 0
            % Usual case. Continue the game with the next click.
        else    
        % If a '0'-field is uncovered, the code starts an autofill process
        % by uncovering the surrounding 8 fields. If another '0' is 
        % uncovered, the coordinates of this field will enter the same 
        % process. The coordinates of '0'-fields are stored in a cell-array
        % called 'list'. The autofill-process will be continued until all
        % '0'-fields resulting from the click have been uncovered.
        
        % Preallocate list at maximum possible size.
        level = getappdata(gcf, 'level');
        list = cell(1, level(1)*level(2));
        
        % Start auto-fill process.
        % Add coordinates of the field that has been clicked on 
        % as first element to 'list'.
        list{1} = [a, b]; 
        % The position of the element within 'list' that is evaluated is
        % initialized with 1.
        pos = 1; 
        
        % Continue in the while-loop, until all elements in 'list' 
        % have entered the autofill process. 
        while pos <= length(list) 
                % Index of the center-field whose neighbors are uncovered.
                idx = list{(pos)};
                % Indices of surrounding field.
                [x1, x2] = ndgrid(-1:1, -1:1);
                    % Loop through the 8 surrounding fields.
                    for i = [1:4, 6:9] 
                        try
                            % the variable 'sum' stores the number of
                            % surrounding mines in the field.
                            sumMines = uncover(idx(1)+x1(i), idx(2)+x2(i));
                            % When a new field that is surrounded by 0 mines 
                            % is found, the coordinates of this field are added
                            % to the 'list' at the next empty position.                       
                            if sumMines == 0
                                % Find the index of the next empty position.
                                last = find(~cellfun(@isempty, list), 1, 'last');
                                % Add coordinates of the field as element to 'list'.
                                list{last+1} = [idx(1)+x1(i), idx(2)+x2(i)];
                                % Trim extra zeros from 'list'.
                                list = list(1:(last+1)); 
                            end
                            % An error occurs, when the field has been already
                            % opened or does not exist, in case the field is at
                            % the borders of the mine field. The error is catched
                            % by the try-catch-loop and the code continues
                            % with the next element of the for-loop.
                        catch                   
                            continue
                        end % try loop.
                    end % for loop.
                    
                    % Start the process for the next element in 'list'.
                    pos = pos+1;
        end % while loop.
        end % if loop.
        
% --------------- The user hits a mine and loses the game. ------------- 

    case 1
        
        % Load and resize new images.
        imgMine = imresize(imread('Mine.jpg'), [20, 20]);
        imgMineR = imresize(imread('MineRed.jpg'), [20, 20]);
        imgMineX = imresize(imread('MineRedCross.jpg'), [20, 20]);
        imgSmileyX = imresize(imread('Smileydead.jpg'), [30, 30]);
        
        % Stop the timer.
        stop(timerfind('name', 'tm'));
        
        % Display all hidden mines.
        % Get the 2d-indices of the mines.
        mineField = getappdata(gcf, 'mineField'); 
        [a, b] = find(mineField==1); 
        
        for i = 1:length(a)
            % Select all fields that cover mines and change image.
            hiddenMines = findobj('UserData', [a(i), b(i)],'Tag','field'); 
            set(hiddenMines, 'CData', imgMine); 
        end
        
        % Mark the field of the mine that has been just hit in red.
        set(src, 'CData', imgMineR);
        
        % Mark incorrectly placed flag-fields.
        try
            % Select indices of all fields with flags.
            flagField = findobj('Tag', 'flag');
            
            for i = 1:length(flagField)
                mine = getappdata(flagField(i), 'Mine');
                % Change image for flags that had been set incorrectly
                % to crossed out mine.
                if mine == 0 
                   set(flagField(i), 'CData', imgMineX);
                end
            end % for loop.
        catch
            % Ignore error that occurs if no flags have been set yet 
            % and continue in code.
        end % try loop.
        
        % Change smiley face to losing face.
        smiley = findobj('Tag', 'smiley');
        set(smiley, 'CData', imgSmileyX);
        
        % Disable all fields and disable WindowButtonFunctions.
        fields = [findobj('Tag', 'field');findobj('Tag', 'flag')];
        set(fields, 'enable', 'inactive', ...
                    'ButtonDownFcn', '');
        set(gcf, 'WindowButtonDownFcn', '', ...
                 'WindowButtonUpFcn', '');
    otherwise
        error('error in mine field');
        
end % switch loop.


function sumMines = uncover(a, b)
% ** function sumMines = uncover(a, b)
% Actions that are performed when a field is uncovered and not mined.
% The number of surrounding mines is displayed in an corresponding color.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% a           double      first index of button within the minefield
% b           double      second index of button within the minefield
%
% <<< OUTPUT VARIABLE <<<
% NAME        TYPE        DESCRIPTION
% sumMines    double      number of surrounding mines

% Find the field corresponding to the input-index.
field = findobj('UserData', [a, b]);

% An error occurs here when no field with the given coordinates is found
% or when the field has been set to an inactive state. The appearance
% of the error is useful for the try-catch-loop during the auto-fill
% process in the function 'leftclick'.
invalidField = (isempty(field)==1) || (strcmp(get(field, 'enable'), 'inactive')==1);

if invalidField
    error('Invalid field');
else
    % Change appearance of the field, set it to an inactive state and
    % delete ButtonDownFcn.
    set(field, 'FontWeight', 'bold', ... 
               'BackgroundColor', [0.85 0.85 0.85], ...
               'Enable', 'inactive', ...
               'ButtonDownFcn', '');
    
    % Evaluate the the number of surrounding mines.
    numberArr = getappdata(gcf, 'numberField');
    sumMines = numberArr(a, b);
    
    % Change the fontcolor according to the displayed number.  
    switch sumMines
        
        case 0
            % no number will be displayed 
            set(field, 'String', '');    
        case 1
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'blue');
        case 2
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'green');
        case 3
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'red');       
        case 4
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'magenta');       
        case 5
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', [0.4 0 0]);        
        case 6
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'cyan');       
        case 7
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', 'black');       
        case 8
            set(field, 'String', int2str(sumMines), ...
                       'ForegroundColor', [0.4 0.4 0.4]); 
        
        otherwise
            error('wrong calculation');
            
    end
    
    % Update the number of fields that still have to be uncovered to win.
    toUncover = getappdata(gcf, 'toUncover');
    toUncover = toUncover-1;
    
%    -------------------- The user wins the game. ----------------------

    % All safe fields have been uncovered.    
    if toUncover == 0   
        
        % Change appearance of the smiley button.
        set(gcf, 'WindowButtonUpFcn', '');
        smiley = findobj('Tag', 'smiley');
        imgSmileyS = imresize(imread('Smileyglasses.jpg'), [30, 30]);
        set(smiley, 'CData', imgSmileyS);
        
        % Stop timer.
        stop(timerfindall);
        
    % There are still uncovered safe fields and the game continues.   
    else
        setappdata(gcf, 'toUncover', toUncover);
    end
end

% ---------------- Local functions regarding right clicks ----------------

function raiseflag(src, eventdata)
% ** function raiseflag(src, eventdata)
% This local function is executed when right-clicking a field. 
% It labels the field with a flag and sets the field into an 
% inactive state. The counter-value is decreased by one, even 
% if the flag has been set incorrectly.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

% Get the counter value.
uiCounter = findobj('Tag', 'counter');
nCount = str2double(get(uiCounter, 'String'));

if nCount == 0;
    % The user is warned, that he has set more flags than mines are hidden.
    % He should find the mistake before continuing.
    warndlg('More flags than mines!');
    
else
    % Decrease the counter-value by 1. Format the display of the number, 
    % so that 3 digits with leading zeros are displayed.
    nCount = sprintf('%03i', nCount-1); 
    set(uiCounter, 'String', nCount);
    
    % Label the field with the flag-image.
    imgFlag = imresize(imread('Flag.jpg'), [20, 20]);
    
    % The ButtonDownFcn is changed, so that the field can be restored.
    % The 'Tag' is changed to 'flag', so that the flagged fields can be
    % found later.
    set(src, 'CData', imgFlag, ...
             'Tag', 'flag', ...
             'Enable','inactive',...
             'ButtonDownFcn', @restore);  
         
end

function restore(src, eventdata)
% ** function restore(src, eventdata)
% This subfunction is executed when right-clicking on a flagged field 
% in order to put the field back in its uncoverable default state.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

% Restore field-properties.
set(src, 'enable', 'on', ...
         'CData', [], ...
         'ButtonDownFcn', @raiseflag, ...
         'Tag', 'field');

% Update the value of the mine counter.
uiCounter = findobj('Tag', 'counter');
nCount = str2double(get(uiCounter, 'String'));
nCount = nCount+1;
set(uiCounter, 'String', sprintf('%03i', nCount));
setsmileyface;


%% --------------------- Various other functions -----------------------

function callbacknewgame(src, eventdata, mRows, nCols, nMines)
% ** function callbacknewgame(src, eventdata, mRows, nCols, nMines)
% This local function is excecuted when the smiley button is left-clicked.
% It points to the main function and takes the same input arguments, 
% additional to the two default arguments for callback-functions.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
% mRows       double      number of rows, height of field
% nCols       double      number of columns, width of field
% nMines      double      number of mines
%
% <<< NO OUTPUT VARIABLES <<<

minesearcher(mRows, nCols, nMines);


function [mRows, nCols, nMines] = checkfieldconfig(r, c, m)
% ** function [mRows, nCols, nMines] = checkfieldconfig(r, c, m)
% This local function checks, if the given arguments are valid values for the game
% settings. The datatype and the size of the numbers are checked. If input
% values are invalid, the function throws an error that is catched by the
% code that calls the function.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% r           double      number of rows to be checked
% c           double      number of columns to be checked
% m           double      number of mines to be checked
%
% <<< OUTPUT VARIABLE <<<
% NAME        TYPE        DESCRIPTION
% mRows       double      number of rows
% nCols       double      number of columns
% nMines      double      number of mines


% The input values are checked for the datatype.
notNumeric = isnan(r) || isnan(c) || isnan(m);
isChar = ischar(r) || ischar(c) || ischar(m);

if notNumeric || isChar
    error('Invalid inputs');
else
    % The entered values have to match the rules of minesearcher.
    % Minimal and maximal field size and maximal number of mines are
    % predefined.
    outOfRange = r<8 || r>24 || c<8 || c>30;
    tooManyMines = m>ceil(r*c/3); 
    if outOfRange || tooManyMines 
        error('Invalid field configuration');
    else
        % Round input values so that decimal values can be accepted and
        % transform them to valid output arguments.
        mRows=round(r);
        nCols=round(c);
        nMines=round(m);
    end
end


function exitfcn(src, eventdata)
% ** function exitfcn(src, eventdata)
% This local function closes the game window, stops and deletes the timer. 
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

% A try-catch loop is used so that the window can be closed
% even if an error occures when deleting the timer.
try
    stop(timerfindall);
    delete(timerfindall);
    delete(gcf);
    
catch
    delete(gcf);
    
end

% ------------------------ Change smiley face -----------------------------

function setsmileyo(src, eventdata)
% ** function setsmileyo(src, eventdata)
% This local function sets the image on the smiley button to the surprised face.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

uiSmiley = findobj('Tag', 'smiley');
imgSmileyO = imresize(imread('SmileyO.jpg'), [30, 30]);
set(uiSmiley, 'CData', imgSmileyO);

function setsmileyface(src, eventdata)
% ** function setsmileyface(src, eventdata)
% This local function sets the image on the smiley button to the regular
% smiley face.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

imgSmiley = imresize(imread('Smiley.jpg'), [30, 30]);
uiSmiley = findobj('Tag', 'smiley');
set(uiSmiley, 'CData', imgSmiley);   

% --------------------------- Costum game menu ----------------------------

function callbackcustom(src, eventdata)
% ** function callbackcustom(src, eventdata)
% This local function generates the window and the GUIs to enter the settings 
% for a customized game.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

% Set size of the window.
sz = [250, 150]; 
% Create figure.
fig2 = figure('name', 'Custom Field', ...
              'NumberTitle', 'off', ...
              'menubar', 'none', ...
              'Position', [0 0 sz(1) sz(2)]);
% Move figure to the center.          
movegui(fig2, 'center');

% Create text-fields for height, width and number of mines.
uiTxt(1) = uicontrol(fig2, 'Position', [0 sz(2)-40 70 25], ...
                           'String', 'Height:');
uiTxt(2) = uicontrol(fig2, 'Position', [0 sz(2)-70 70 25], ...
                           'String', 'Width:');
uiTxt(3) = uicontrol(fig2, 'Position', [0 sz(2)-100 70 25], ...
                           'String', 'Mines:');            
set(uiTxt, 'Style', 'text');

% Create edit-fields for entering values of width, heigth and number of mines.
uiValue(1) = uicontrol(fig2, 'Position', [70 sz(2)-40 50 25]);
uiValue(2) = uicontrol(fig2, 'Position', [70 sz(2)-70 50 25]);
uiValue(3) = uicontrol(fig2, 'Position', [70 sz(2)-100 50 25]);
set(uiValue, 'Style', 'edit');

% Create the OK button that transfers the entered values to the new game.
% The callback is stored in the function callbackok(src, eventdata,
% uiValue).
uicontrol(fig2, 'Style', 'pushbutton', ...
                'String', 'OK', ...
                'Position', [140 sz(2)-40 60 25], ...
                'Callback', {@callbackok, uiValue});

% Create cancel button.
uicontrol(fig2, 'Style', 'pushbutton', ...
                'String', 'Cancel', ...
                'Position', [140 sz(2)-100 60 25], ...
                'Callback', 'close gcf');

            
function callbackok(src, eventdata, uiValue)
% ** function callbackok(src, eventdata, uiValue)
% This local function is executed when the OK button in the Custom Field menu
% is pressed. Errors will be displayed when no numeric values are entered,
% or the field size or number of mines exceeds the presetted values.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
% uiValue     UIControl   1x3 array storing the UIControls in which
%                         the customized settings had been entered
%
% <<< NO OUTPUT VARIABLES <<<

% Read out the entered values in the 3 text fields and convert them to
% a list of doubles.
a = str2double(get(uiValue, 'string'));

% Check if the entered values are valid. An error occurs if they are
% not valid for the field configuration. This error is catched by a
% warn-dialogue and the user can type in new values.
try 
    [mRows, nCols, nMines]=checkfieldconfig(a(1), a(2), a(3));
    % Start a new game with the customized settings.
    close gcf;
    minesearcher(mRows, nCols, nMines);
catch
    warndlg(sprintf(['Please enter three valid numbers!\n' ...
                     'The minimal field size is 8x8\n' ...
                     'and the maximal field size is 24x30.\n' ...
                     'The maxial number of mines is 1/3 of fields!']), ...
                     'Invalid Input');
end



%% ------- Functions regarding the timer ----------------------------------

function timerstart(src, eventdata)
% ** timerstart(src, eventdata)
% This local function sets the initial value of the timer to 0.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

uiTimer = findobj('Tag', 'uiTimer');
global T
T = 0;
set(uiTimer, 'String', sprintf('%03i', T));


function timerupdater(src, eventdata)
% ** function timerupdater(src, eventdata)
% This local function is callback-function of the timer which updates 
% the timer every second.
%
% >>> INPUT VARIABLES >>>
% NAME        TYPE        DESCRIPTION
% src         UIControl   object that called the function
%                         default argument for callback-function
% eventdata   ActionData  default argument for callback-function
%
% <<< NO OUTPUT VARIABLES <<<

uiTimer = findobj('Tag', 'uiTimer');
global T
set(uiTimer, 'String', sprintf('%03i', T));
T = T+1;