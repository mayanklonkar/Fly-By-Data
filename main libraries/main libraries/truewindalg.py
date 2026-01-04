# ============================================================================
# File Name:        truewindalg.py
# Author:           Vivek23
# Description:      Convert Raw Wind Speed to True Wind Speed
# Dependencies:     Python >= 3.8
#                       - numpy     (pip install numpy)
# ============================================================================


import numpy as np

# rotation matrix
def euler2rotmat(roll,pitch,yaw):

    cos_roll    = np.cos(roll)
    sin_roll    = np.sin(roll)
    cos_pitch   = np.cos(pitch)
    sin_pitch   = np.sin(pitch)
    cos_yaw     = np.cos(yaw)
    sin_yaw     = np.sin(yaw)

    T11 = cos_pitch * cos_yaw
    T12 = cos_pitch * sin_yaw
    T13 = -1 * sin_pitch
    T21 = (sin_roll * sin_pitch * cos_yaw) - (cos_roll * sin_yaw)
    T22 = (sin_roll * sin_pitch * sin_yaw) + (cos_roll * cos_yaw)
    T23 = sin_roll * cos_pitch
    T31 = (cos_roll * sin_pitch * cos_yaw) + (sin_roll * sin_yaw)
    T32 = (cos_roll * sin_pitch * sin_yaw) - (sin_roll * cos_yaw)
    T33 = cos_roll * cos_pitch

    R = [[T11,T21,T31],
         [T12,T22,T32],
         [T13,T23,T33]]

    return R


# convert vectors from body to ned using rotation matrix
def body2ned(body_velocity, roll, pitch, yaw):

    R = euler2rotmat(roll, pitch, yaw)

    ned_velocity = np.dot(R, body_velocity)
    
    return ned_velocity


# convert vectors from ned to body using rotation matrix
def ned2body(body_velocity, roll, pitch, yaw):

    R = euler2rotmat(roll, pitch, yaw)
    R_T = [[R[j][i] for j in range(len(R))] for i in range(len(R[0]))]
    body_velocity = np.dot(R_T, body_velocity)
    
    return body_velocity


# relative wind speed algorithm
def truewindest(uvector,vvector,wvector,winddirection,roll,pitch,yaw,vn,ve,vd,rollrate,pitchrate,yawrate,deg2rad):
    
    if deg2rad == 1:
        roll        = np.radians(roll)
        pitch       = np.radians(pitch)
        yaw         = np.radians(yaw)
        rollrate    = np.radians(rollrate) 
        pitchrate   = np.radians(pitchrate) 
        yawrate     = np.radians(yawrate)
    
    wind_vec_body   = np.column_stack([uvector,vvector,wvector])
    vehicle_vec_ned = np.column_stack([vn,ve,vd])

    vehicle_vec_body = []
    for i in range(0,len(roll)):
        vehicle_vec_body.append(ned2body(vehicle_vec_ned[i],roll[i],pitch[i],yaw[i]))
    vehicle_vec_body        = np.array(vehicle_vec_body)

    sh_vec                  = [0,0,1]
    euler_rates_vec         = np.column_stack([rollrate,pitchrate,yawrate])
    angular_velocity_body   = np.cross(euler_rates_vec,sh_vec)
    
    rel_wind_body           = wind_vec_body - vehicle_vec_body - angular_velocity_body

    rel_wind_ned    = []
    rel_wind_ned_2d = []

    for i in range(0,len(roll)):
        rel_wind_ned.append(body2ned(rel_wind_body[i],roll[i],pitch[i],yaw[i]))
        rel_wind_ned_2d.append(rel_wind_ned[i][:2])
    
    rel_wind_ned    = np.array(rel_wind_ned)
    rel_wind        = np.linalg.norm(rel_wind_ned,axis=1)
    rel_wind_2d     = np.linalg.norm(rel_wind_ned_2d,axis=1)

    return rel_wind_ned,rel_wind,rel_wind_2d

