package com.example.demo.mapper;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.springframework.stereotype.Repository;

import com.example.demo.model.EstimateGridSensorDataModel;
import com.example.demo.model.SensorGridModel;

@Mapper
@Repository
public interface CmapMapper {
	List<SensorGridModel> getSensorGrid();
	
	List<EstimateGridSensorDataModel> getEstimateGridSensorData();
}
