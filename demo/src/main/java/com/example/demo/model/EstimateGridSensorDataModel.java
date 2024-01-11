package com.example.demo.model;

import lombok.Builder;
import lombok.Data;

@Builder @Data
public class EstimateGridSensorDataModel {
	private int m_id;
	private int m_name;
	private float center_lot;
	private float center_lat;
	private float wd;
	private float ws;
	private float vec_x;
	private float vec_y;
	private String date;
}
