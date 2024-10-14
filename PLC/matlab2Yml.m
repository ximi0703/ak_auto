%%  用于自动生成matlab标定结果对应的yml参数文件(给opencv端使用)
% -- 默认matlab变量名称为 stereoParams 

%% 保存相机内参数据
% 相机1
M1 = [0,0,0;
      0,0,0;
      0,0,1];
M1(1,1) = stereoParams.CameraParameters1.FocalLength(1,1);
M1(2,2) = stereoParams.CameraParameters1.FocalLength(1,2);
M1(1,3) = stereoParams.CameraParameters1.PrincipalPoint(1,1);
M1(2,3) = stereoParams.CameraParameters1.PrincipalPoint(1,2);
D1 = zeros(1,5);
D1(1,1) = stereoParams.CameraParameters1.RadialDistortion(1,1);
D1(1,2) = stereoParams.CameraParameters1.RadialDistortion(1,2);
D1(1,3) = stereoParams.CameraParameters1.TangentialDistortion(1,1);
D1(1,4) = stereoParams.CameraParameters1.TangentialDistortion(1,2);
D1(1,5) = stereoParams.CameraParameters1.RadialDistortion(1,3);
matlab2opencv( M1, 'intrinsics_Current.yml', 'w');
matlab2opencv( D1, 'intrinsics_Current.yml', 'a');

% 相机2
M2 = [0,0,0;
      0,0,0;
      0,0,1];
M2(1,1) = stereoParams.CameraParameters2.FocalLength(1,1);
M2(2,2) = stereoParams.CameraParameters2.FocalLength(1,2);
M2(1,3) = stereoParams.CameraParameters2.PrincipalPoint(1,1);
M2(2,3) = stereoParams.CameraParameters2.PrincipalPoint(1,2);
D2 = zeros(1,5);
D2(1,1) = stereoParams.CameraParameters2.RadialDistortion(1,1);
D2(1,2) = stereoParams.CameraParameters2.RadialDistortion(1,2);
D2(1,3) = stereoParams.CameraParameters2.TangentialDistortion(1,1);
D2(1,4) = stereoParams.CameraParameters2.TangentialDistortion(1,2);
D2(1,5) = stereoParams.CameraParameters2.RadialDistortion(1,3);
matlab2opencv( M2, 'intrinsics_Current.yml', 'a');
matlab2opencv( D2, 'intrinsics_Current.yml', 'a');


%% 保存R/T数据
% matlab 存储数据是列优先, opencv是行优先, 需要转置
R = stereoParams.RotationOfCamera2';
T = stereoParams.TranslationOfCamera2';
matlab2opencv( R, 'extrinsics_Current.yml', 'w');
matlab2opencv( T, 'extrinsics_Current.yml', 'a');
disp('export yml files done.')

function matlab2opencv( variable, fileName, flag)
 
[rows cols] = size(variable);
 
% Beware of Matlab's linear indexing
variable = variable';
 
% Write mode as default
if ( ~exist('flag','var') )
    flag = 'w';
end
 
if ( ~exist(fileName,'file') || flag == 'w' )
    % New file or write mode specified
    file = fopen( fileName, 'w');
    fprintf( file, '%%YAML:1.0\n');
    fprintf( file, '---\n');
else
    % Append mode
    file = fopen( fileName, 'a');
end
 
% Write variable header
fprintf( file, '%s: !!opencv-matrix\n', inputname(1));
fprintf( file, '    rows: %d\n', rows);
fprintf( file, '    cols: %d\n', cols);
fprintf( file, '    dt: d\n');
fprintf( file, '    data: [ ');
 
% Write variable data
for i=1:rows*cols
    fprintf( file, '%.18f', variable(i));
    if (i == rows*cols), break, end
    fprintf( file, ', ');
    if mod(i,3) == 0
        fprintf( file, '\n            ');
    end
end
 
fprintf( file, ']\n');
 
fclose(file);

end


