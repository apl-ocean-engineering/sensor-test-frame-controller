

proto: imu/imu_data_pb2.py

imu/imu_data_pb2.py:  imu/proto/imu_data.proto
	python3 -m grpc_tools.protoc -I imu/proto/ \
	 			--python_out=imu/ \
	 			--grpc_python_out=imu/ \
	  			imu/proto/imu_data.proto

clean:
	rm -f imu/*pb2.py

.PHONY: proto clean
