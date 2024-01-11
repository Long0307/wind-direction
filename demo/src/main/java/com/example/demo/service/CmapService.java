package com.example.demo.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.mapper.CmapMapper;
import com.example.demo.model.EstimateGridSensorDataModel;
import com.example.demo.model.SensorGridModel;

@Service
public class CmapService {
	
	@Autowired
	private CmapMapper cmapMapper;
	
	public List<SensorGridModel> getSensorGrid(){
		return cmapMapper.getSensorGrid();
	}
	
	public List<EstimateGridSensorDataModel> getEstimateGridSensorData(){
		return cmapMapper.getEstimateGridSensorData();
	}
}
