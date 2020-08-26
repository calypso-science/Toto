


from ...core.toolbox import get_number_of_loops,degToCompass


def do_EVA_general(time,mag,tp,drr,tm,
            dir_interval,threshold_type,directional_pot,min_time,time_blocking,display,Hmax_RPV,water_depth,folderout):

    ## Input
    sint=(time[2]-time[1]).seconds/(3600)
    month=time.month
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)


if ~isempty(tp) && all(tp(~isnan(tp))*10==round(tp(~isnan(tp))*10))%check if tp values contain only one decimal
    tp=tp-.05+.1*rand(length(tp),1);%give a random value between tp+/-0.05
end


if isempty(drr)
    directional_data=mag;
else
    directional_data=NaN(length(mag),length(directional_interval));
    directional_data(:,end)=mag;
    for j=1:length(directional_interval)-1
        if directional_interval(j+1) <= directional_interval(j)
            index=find(mod(drr,360)>directional_interval(j) | mod(drr,360)<=directional_interval(j+1));
        else
            index=find(mod(drr,360)>directional_interval(j) & mod(drr,360)<=directional_interval(j+1));
        end
        directional_data(index,j)=mag(index);
        clear index
    end
    clear j
end



for i=1:size(directional_data,2)
    maxi=[];maxi_index=[];time_index=[];Hmp1=[];Cmp1=[];LnN1=[];
    if ~isempty(drr);drr_index=[];end
    if ~isempty(tp);tp_index=[];end
    
    for j=1:number_of_loops
        if time_blocking_POT
            switch time_blocking{1}
                case 'All'
                    month_identifier=annual_months;
                case 'Seasonal'
                    month_identifier=season.months{j};
                case 'Monthly'
                    month_identifier=months(j);
            end
        else
            month_identifier=annual_months;
        end
        if directional_pot %find peaks for each direction range separately
            dir_data=directional_data(:,i);
        else%non-directional POT
            dir_data=directional_data(:,end);
        end
        index_month=ismember(month,month_identifier);
        dir_data(~index_month)=NaN;
        
        [maxi0,maxi_index0]=P_O_T(dir_data,sint,threshold,duration,threshold_type);
        if ~directional_pot && size(directional_data,2)>1 && i~=size(directional_data,2)%attribute peaks for each direction range separately
               if directional_interval(i+1) <= directional_interval(i)
             index_to_keep=find(mod(drr(maxi_index0),360)>directional_interval(i) | mod(drr(maxi_index0),360)<=directional_interval(i+1));
               else
                     index_to_keep=find(mod(drr(maxi_index0),360)>directional_interval(i) & mod(drr(maxi_index0),360)<=directional_interval(i+1));
               end
               maxi0=maxi0(index_to_keep);
               maxi_index0=maxi_index0(index_to_keep);
        end
        if Hmax_RPV  %calcualtes most probable max wave height (assuming a storm cannot last moret than 48h)
            [Hmp0,Cmp0,LnN0]=calc_Hmp(dir_data,maxi_index0,tm,depth,48,sint);
            Hmp1=[Hmp1; Hmp0(:)];
            Cmp1=[Cmp1; Cmp0(:)];
            LnN1=[LnN1; LnN0(:)];
        end

        maxi=[maxi; maxi0(:)];
        maxi_index=[maxi_index; maxi_index0(:)];
        time_index=[time_index; time(maxi_index0)];
        
    end
    maximums{i}=maxi;
    max_index{i}=maxi_index;
    time_peaks{i}=time_index;
    if Hmax_RPV
        Hmp{i}=Hmp1;
        Cmp{i}=Cmp1;
        LnN{i}=LnN1;
    end
    
    if ~isempty(drr)
        drr_peaks{i}=[drr_index drr(max_index{i})];
    end
    if ~isempty(tp)
        tp_peaks{i}=[tp_index tp(max_index{i})];
    end
end

clear i j

if size(directional_data,2)>1 %regroup the directional peaks on the same time series
    maximums_direction_dependent=cat(1,maximums{1:end-1});
    time_peaks_direction_dependent=cat(1,time_peaks{1:end-1});
end

switch threshold_type
    case 'percentile'
        datacopy=sort(denan(mag(:)));
        thresh=datacopy(round(length(datacopy)*(threshold/100)));
        clear datacopy
    otherwise
        thresh=threshold;
end

if view_peaks
    figure
    h = zoom;
    if ~exist('maximums_direction_dependent','var') || ~directional_pot
        plot(time,mag)
        hold on
        p=plot(time_peaks{end},maximums{end},'r+');%omni-directional peaks
        p2=plot(time_peaks{end}([1 end]),[thresh thresh],'-g');
        legend([p p2],'Omni-directional peaks','Threshold')
        set(h,'Enable','on');
        datetick('x','mmm/yy','keepticks')
        zoomAdaptiveDateTicks('on')
        ylabel(mag_name)
        title({file_name;'(press any key to close figure)'})
    else
        subplot(2,1,1)
        plot(time,mag)
        hold on
        p=plot(time_peaks{end},maximums{end},'r+');%omni-directional peaks
        p2=plot(time_peaks{end}([1 end]),[thresh thresh],'-g');
        legend([p p2],'Omni-directional peaks','Threshold')
        set(h,'Enable','on');
        datetick('x','mmm/yy','keepticks')
        ylabel(mag_name)
        title({file_name;'(press any key to close figure)'})
        subplot(2,1,2)
        plot(time,mag)
        hold on
        p=plot(time_peaks_direction_dependent,maximums_direction_dependent,'r+');%direction dependent peaks
        legend(p,'Directional peaks')
        set(h,'Enable','on');
        datetick('x','mmm/yy','keepticks')
        zoomAdaptiveDateTicks('on')
        ylabel(mag_name)
    end
    pause
    close
end

%save the peaks and corresponding directions

Var_peaks=cell(size(directional_data,2),7);
for j=1:size(directional_data,2) %Add directional peaks
    if ~isempty(time_peaks{j})
        Var_peaks{j,1}(:,1)=time_peaks{j};% Save the time
        if  ~isempty(tp)
            Var_peaks{j,1}(:,2)=maximums{j};%Save the data
            Var_peaks{j,1}(:,3)=tp_peaks{j};%Save the data
            if exist('Hmp','var');Var_peaks{j,1}(:,4)=Hmp{j};
                Var_peaks{j,1}(:,5)=Cmp{j};
                Var_peaks{j,1}(:,6)=LnN{j};
            end%Save the data
        else
            Var_peaks{j,1}(:,2)=maximums{j};%Save the data
            if exist('Hmp','var');Var_peaks{j,1}(:,4)=Hmp{j};
                Var_peaks{j,1}(:,5)=Cmp{j};
                Var_peaks{j,1}(:,6)=LnN{j};
            end
        end
    end
    if j==size(directional_data,2)
        if ~isempty(tp)
            Var_peaks{j,2}=[varargin{1}{1,3},' peaks omni']; %save the name of the variable
        else
            Var_peaks{j,2}=[varargin{1}{1,3},' ',varargin{1}{3,3},' peaks omni']; %save the name of the variable
        end
    else
        if ~isempty(tp)
            Var_peaks{j,2}=[varargin{1}{1,3},' peaks ',num2str(directional_interval(j)),'-',num2str(directional_interval(j+1))]; %save the name of the variable
        else
            Var_peaks{j,2}=[varargin{1}{1,3},' ',varargin{1}{3,3},' peaks ',num2str(directional_interval(j)),'-',num2str(directional_interval(j+1))]; %save the name of the variable
        end
    end
    Var_peaks{j,3}=varargin{1}{1,4}; %save the type
    Var_peaks{j,4}=varargin{1}{1,6}; %save the name of the file
    Var_peaks{j,5}=varargin{1}{1,7};% save the unit of mag
    idx=1;
    if ~isempty(tp)
        Var_peaks{j,5+idx}=varargin{1}{2,7}; %save the unit
        idx=idx+1;
    end
    Var_peaks{j,5+idx}=varargin{1}{3,7}; %save the name of the file
end


EVA_all(Var_peaks,varargin{1},time_blocking,time_blocking_POT)
