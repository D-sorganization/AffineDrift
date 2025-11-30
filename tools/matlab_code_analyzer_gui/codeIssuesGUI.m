function T = codeIssuesGUI(varargin)
%CODEISSUESGUI Interactive GUI for MATLAB Code Analyzer with file/folder selection.
%
%   T = CODEISSUESGUI() opens a GUI allowing users to select files or
%   folders for code analysis using MATLAB's Code Analyzer (MLint).
%
%   T = CODEISSUESGUI('Name', Value, ...) accepts these options:
%       'DefaultPath'   - Initial directory to show in file browser
%       'Output'        - Output file path. If omitted, user will be prompted.
%       'AutoSave'      - true|false (default false). If true, automatically
%                         saves results to a timestamped file.
%       'Recursive'     - true|false (default true). Only relevant if
%                         selecting folders.
%       'IncludeExt'    - Cellstr of file extensions to include. Default {'.m'}
%       'ExcludeDirs'   - Cellstr of directory names to skip
%       'ExcludeFiles'  - Cellstr of wildcard file patterns to skip
%       'OnError'       - 'record' (default) | 'rethrow'
%       'ShowProgress'  - true|false (default true). Shows progress dialog.
%
%   The returned table has the same format as exportCodeIssues:
%       File        - Absolute file path
%       RelFile     - Relative file path
%       Line        - Line number (double)
%       Column      - Column number (double)
%       Identifier  - Code Analyzer message identifier (string)
%       Message     - Human-readable message text (string)
%
%   Example:
%       % Open GUI for interactive code analysis
%       issues = codeIssuesGUI();
%
%       % Start in a specific directory
%       issues = codeIssuesGUI('DefaultPath', 'C:\MyProject\src');
%
%   See also: EXPORTCODEISSUES, CHECKCODE

% Parse inputs
p = inputParser;
p.addParameter('DefaultPath', pwd, @(s)ischar(s) || isstring(s));
p.addParameter('Output', '', @(s)ischar(s) || isstring(s));
p.addParameter('AutoSave', false, @(x)islogical(x) && isscalar(x));
p.addParameter('Recursive', true, @(x)islogical(x) && isscalar(x));
p.addParameter('IncludeExt', {'.m'}, @(c)iscellstr(c) || isstring(c));
p.addParameter('ExcludeDirs', {}, @(c)iscellstr(c) || isstring(c));
p.addParameter('ExcludeFiles', {}, @(c)iscellstr(c) || isstring(c));
p.addParameter('OnError', 'record', @(s)any(strcmpi(s,{'record','rethrow'})));
p.addParameter('ShowProgress', true, @(x)islogical(x) && isscalar(x));
p.parse(varargin{:});
opts = p.Results;

% Convert strings to char for compatibility
opts.DefaultPath = char(opts.DefaultPath);
opts.Output = char(opts.Output);
opts.IncludeExt = cellstr(opts.IncludeExt);
opts.ExcludeDirs = cellstr(opts.ExcludeDirs);
opts.ExcludeFiles = cellstr(opts.ExcludeFiles);

% Validate inputs
if ~isfolder(opts.DefaultPath)
    error('codeIssuesGUI:InvalidPath', 'DefaultPath must be a valid directory: %s', opts.DefaultPath);
end

% Create GUI
fig = figure('Name', 'MATLAB Code Analyzer', ...
             'NumberTitle', 'off', ...
             'MenuBar', 'none', ...
             'Toolbar', 'none', ...
             'Resize', 'on', ...
             'Position', [100, 100, 600, 500], ...
             'CloseRequestFcn', @cancelDialog);

% Create UI controls
% Path listbox and controls
uicontrol('Style', 'text', 'String', 'Selected Paths:', ...
          'HorizontalAlignment', 'left', ...
          'Position', [20, 450, 100, 20]);

pathListbox = uicontrol('Style', 'listbox', ...
                       'Position', [20, 300, 400, 140], ...
                       'String', {}, ...
                       'Value', 1, ...
                       'Max', 2); % Allow multiple selection

uicontrol('Style', 'pushbutton', 'String', 'Add Files', ...
          'Position', [430, 420, 80, 25], ...
          'Callback', @addFiles);

uicontrol('Style', 'pushbutton', 'String', 'Add Folder', ...
          'Position', [430, 385, 80, 25], ...
          'Callback', @addFolder);

uicontrol('Style', 'pushbutton', 'String', 'Remove', ...
          'Position', [430, 350, 80, 25], ...
          'Callback', @removePath);

uicontrol('Style', 'pushbutton', 'String', 'Clear All', ...
          'Position', [430, 315, 80, 25], ...
          'Callback', @clearAll);

% Analysis options
uicontrol('Style', 'text', 'String', 'Analysis Options:', ...
          'HorizontalAlignment', 'left', ...
          'Position', [20, 270, 120, 20]);

recursiveCheckbox = uicontrol('Style', 'checkbox', ...
                             'String', 'Recursive search', ...
                             'Value', opts.Recursive, ...
                             'Position', [30, 245, 120, 20]);

% Output options
uicontrol('Style', 'text', 'String', 'Output Options:', ...
          'HorizontalAlignment', 'left', ...
          'Position', [200, 270, 100, 20]);

outputEdit = uicontrol('Style', 'edit', ...
                      'String', opts.Output, ...
                      'Position', [200, 220, 300, 25]);

uicontrol('Style', 'pushbutton', 'String', 'Browse...', ...
          'Position', [510, 220, 60, 25], ...
          'Callback', @browseOutput);

autoSaveCheckbox = uicontrol('Style', 'checkbox', ...
                           'String', 'Auto-save with timestamp', ...
                           'Value', opts.AutoSave, ...
                           'Position', [200, 190, 150, 20]);

% Progress option
showProgressCheckbox = uicontrol('Style', 'checkbox', ...
                               'String', 'Show progress', ...
                               'Value', opts.ShowProgress, ...
                               'Position', [200, 160, 100, 20]);

% Action buttons
uicontrol('Style', 'pushbutton', 'String', 'Analyze', ...
          'Position', [200, 50, 80, 30], ...
          'Callback', @runAnalysis, ...
          'FontWeight', 'bold');

uicontrol('Style', 'pushbutton', 'String', 'Cancel', ...
          'Position', [300, 50, 80, 30], ...
          'Callback', @cancelDialog);

% Store data
currentPaths = {};
analysisOpts = struct();

% Wait for dialog to close
uiwait(fig);

% Return results
T = analysisOpts;

    function addFiles(~, ~)
        [files, path] = uigetfile({'*.m', 'MATLAB Files (*.m)'; ...
                                  '*.*', 'All Files (*.*)'}, ...
                                  'Select MATLAB files', opts.DefaultPath, 'MultiSelect', 'on');

        if ~isequal(files, 0)
            if ischar(files)
                files = {files};
            end

            for i = 1:length(files)
                fullPath = fullfile(path, files{i});
                if ~any(strcmp(currentPaths, fullPath))
                    currentPaths{end+1} = fullPath; %#ok<AGROW>
                end
            end

            updatePathList();
        end
    end

    function addFolder(~, ~)
        path = uigetdir(opts.DefaultPath, 'Select MATLAB folder');

        if ~isequal(path, 0) && ~any(strcmp(currentPaths, path))
            currentPaths{end+1} = path; %#ok<AGROW>
            updatePathList();
        end
    end

    function removePath(~, ~)
        selected = get(pathListbox, 'Value');
        if ~isempty(selected) && selected <= length(currentPaths)
            currentPaths(selected) = [];
            updatePathList();
        end
    end

    function clearAll(~, ~)
        currentPaths = {};
        updatePathList();
    end

    function updatePathList()
        if isempty(currentPaths)
            set(pathListbox, 'String', {}, 'Value', 1);
        else
            set(pathListbox, 'String', currentPaths, 'Value', min(get(pathListbox, 'Value'), length(currentPaths)));
        end
    end

    function browseOutput(~, ~)
        [file, path] = uiputfile({'*.csv', 'CSV Files (*.csv)'; ...
                                '*.xlsx', 'Excel Files (*.xlsx)'; ...
                                '*.json', 'JSON Files (*.json)'; ...
                                '*.md', 'Markdown Files (*.md)'}, ...
                                'Save analysis results', 'code_issues.csv');

        if ~isequal(file, 0)
            set(outputEdit, 'String', fullfile(path, file));
        end
    end

    function runAnalysis(~, ~)
        % Gather options
        analysisOpts.DefaultPath = opts.DefaultPath;
        analysisOpts.OutputFile = get(outputEdit, 'String');
        analysisOpts.AutoSave = get(autoSaveCheckbox, 'Value');
        analysisOpts.Recursive = get(recursiveCheckbox, 'Value');
        analysisOpts.IncludeExt = opts.IncludeExt;
        analysisOpts.ExcludeDirs = opts.ExcludeDirs;
        analysisOpts.ExcludeFiles = opts.ExcludeFiles;
        analysisOpts.OnError = opts.OnError;
        analysisOpts.ShowProgress = get(showProgressCheckbox, 'Value');
        analysisOpts.Paths = currentPaths;

        % Close dialog
        delete(fig);

        % Run analysis if paths selected
        if isempty(currentPaths)
            warning('codeIssuesGUI:NoPaths', 'No files or folders selected for analysis.');
            T = table();
            return;
        end

        % Call exportCodeIssues with gathered options
        try
            T = exportCodeIssues(...
                'Paths', currentPaths, ...
                'Recursive', analysisOpts.Recursive, ...
                'IncludeExt', analysisOpts.IncludeExt, ...
                'ExcludeDirs', analysisOpts.ExcludeDirs, ...
                'ExcludeFiles', analysisOpts.ExcludeFiles, ...
                'OnError', analysisOpts.OnError, ...
                'ShowProgress', analysisOpts.ShowProgress);

            fprintf('[codeIssuesGUI] Analysis complete: %d issues found\n', height(T));
        catch ME
            warning('codeIssuesGUI:AnalysisFailed', 'Analysis failed: %s', ME.message);
            T = table();
        end

        % Handle output
        if ~isempty(analysisOpts.OutputFile) || analysisOpts.AutoSave
            outputFile = analysisOpts.OutputFile;
            if isempty(outputFile) && analysisOpts.AutoSave
                timestamp = char(datetime('now', 'Format', 'yyyyMMdd_HHmmss'));
                outputFile = fullfile(pwd, sprintf('code_issues_%s.csv', timestamp));
            end

            if ~isempty(outputFile)
                try
                    % Write results table to file using writeOutput function
                    writeOutput(T, outputFile, pwd);
                    fprintf('[codeIssuesGUI] Results saved to: %s\n', outputFile);
                catch ME
                    fprintf('[codeIssuesGUI] Warning: Could not save to %s: %s\n', outputFile, ME.message);
                end
            end
        end

        % Show summary
        if analysisOpts.ShowProgress && height(T) > 0
            fprintf('\nTip: Results are also returned as a table variable.\n');
            fprintf('     Results are automatically saved to workspace as ''codeAnalysisResults''.\n');
        end

        % Optionally assign to base workspace
        try
            assignin('base', 'codeAnalysisResults', T);
        catch
            % Silent fail if workspace assignment doesn't work
        end
    end

    function cancelDialog(~, ~)
        analysisOpts = struct(); % Empty struct indicates cancellation
        delete(fig);
    end
end

function writeOutput(T, outPath, root)
    outPath = char(string(outPath));
    [outDir,~,ext] = fileparts(outPath);
    if ~isempty(outDir) && ~isfolder(outDir)
        mkdir(outDir);
    end
    ext = lower(ext);
    switch ext
        case '.csv'
            writetable(T, outPath);
        case '.xlsx'
            writetable(T, outPath, 'FileType','spreadsheet');
        case '.json'
            % Convert to struct array with sensible field names
            S = table2struct(T);
            % Use PrettyPrint if available (R2021a+), otherwise use basic jsonencode
            try
                txt = jsonencode(S, 'PrettyPrint', true);
            catch
                txt = jsonencode(S);
            end
            fid = fopen(outPath, 'w', 'n','UTF-8');
            assert(fid>0, 'codeIssuesGUI:IO', 'Could not open %s for writing.', outPath);
            cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>
            fwrite(fid, txt, 'char');
        case '.md'
            fid = fopen(outPath, 'w', 'n','UTF-8');
            assert(fid>0, 'codeIssuesGUI:IO', 'Could not open %s for writing.', outPath);
            cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>
            fprintf(fid, '# Code Issues Report\n\n');
            fprintf(fid, '**Root:** %s\n\n', root);
            fprintf(fid, '| RelFile | Line | Column | Identifier | Message |\n');
            fprintf(fid, '|:--|--:|--:|:--|:--|\n');
            for i = 1:height(T)
                fprintf(fid, '| %s | %s | %s | %s | %s |\n', ...
                    escapeMd(T.RelFile(i)), num2strOrEmpty(T.Line(i)), ...
                    num2strOrEmpty(T.Column(i)), escapeMd(T.Identifier(i)), ...
                    escapeMd(T.Message(i)) );
            end
        otherwise
            error('codeIssuesGUI:BadExt', 'Unsupported output extension: %s', ext);
    end
end

function s = escapeMd(str)
    s = char(str);
    % Escape backslashes first, then pipes (order matters)
    s = strrep(s, '\', '\\');
    s = strrep(s, '|', '\|');
    s = regexprep(s, '[\r\n]+', ' ');
end

function s = num2strOrEmpty(v)
    if isnan(v)
        s = '';
    else
        s = num2str(v);
    end
end
