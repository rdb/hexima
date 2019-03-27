#version 150

#pragma include "common.glsl"

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 vertex;
in vec3 normal;
in vec3 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec3 vpos;
out vec3 norm;
out vec4 shad[1];
out vec3 col;
out vec2 uv;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * vertex;
  vpos = vec3(p3d_ModelViewMatrix * vertex);
  norm = normalize(p3d_NormalMatrix * normal);
  shad[0] = p3d_LightSource[0].shadowViewMatrix * vec4(vpos, 1);
  col = p3d_Color;
  uv = p3d_MultiTexCoord0;
}
