#version 150

#pragma include "common.glsl"

uniform sampler2D p3d_Texture0;

uniform struct p3d_LightModelParameters {
  vec4 ambient;
} p3d_LightModel;

uniform struct p3d_MaterialParameters {
  vec4 ambient;
  vec4 diffuse;
  vec3 specular;
  float roughness;
} p3d_Material;

const vec3 fog_color = vec3(0.31, 0.42, 0.53);

in vec3 vpos;
in vec3 norm;
in vec4 shad[1];
in vec3 col;
in vec2 uv;

uniform vec4 p3d_ColorScale;
uniform vec4 p3d_TexAlphaOnly;

out vec4 p3d_FragColor;

void main() {
  p3d_FragColor = p3d_LightModel.ambient * p3d_Material.diffuse;

  float alpha = p3d_Material.roughness * p3d_Material.roughness;
  vec3 N = norm;

  //for (int i = 0; i < p3d_LightSource.length(); ++i) {
#define i 0
    vec3 diff = p3d_LightSource[i].position.xyz - vpos * p3d_LightSource[i].position.w;
    vec3 L = normalize(diff);
    vec3 V = normalize(-vpos);
    vec3 H = normalize(L + V);

    float NdotL = clamp(dot(N, L), 0.001, 1.0);
    float NdotV = clamp(abs(dot(N, V)), 0.001, 1.0);
    float NdotH = clamp(dot(N, H), 0.0, 1.0);
    float VdotH = clamp(dot(V, H), 0.0, 1.0);

    // Specular term
    float reflectance = max(max(p3d_Material.specular.r, p3d_Material.specular.g), p3d_Material.specular.b);
    float reflectance90 = clamp(reflectance * 25.0, 0.0, 1.0);
    vec3 F = p3d_Material.specular + (vec3(reflectance90) - reflectance) * pow(clamp(1.0 - VdotH, 0.0, 1.0), 5.0);

    // Geometric occlusion term
    float alpha2 = alpha * alpha;
    float attenuationL = 2.0 * NdotL / (NdotL + sqrt(alpha2 + (1.0 - alpha2) * (NdotL * NdotL)));
    float attenuationV = 2.0 * NdotV / (NdotV + sqrt(alpha2 + (1.0 - alpha2) * (NdotV * NdotV)));
    float G = attenuationL * attenuationV;

    // Microfacet distribution term
    float f = (NdotH * alpha2 - NdotH) * NdotH + 1.0;
    float D = alpha2 / (M_PI * f * f);

    // Lambert, energy conserving
    vec3 diffuseContrib = (1.0 - F) * p3d_Material.diffuse.rgb / M_PI;

    // Cook-Torrance
    vec3 specContrib = F * G * D / (4.0 * NdotL * NdotV);

    // Obtain final intensity as reflectance (BRDF) scaled by the energy of the light (cosine law)
    vec3 color = p3d_LightSource[i].color * 4.5 * (diffuseContrib + specContrib) * col;
    color *= (textureProj(p3d_LightSource[i].shadowMap, shad[i]) * NdotL) * 0.9 + 0.1;

    p3d_FragColor.rgb += color;
  //}

  vec4 texcol = texture(p3d_Texture0, uv) + p3d_TexAlphaOnly;
  p3d_FragColor.rgb *= texcol.rgb;

  p3d_FragColor.rgb *= p3d_ColorScale.rgb;

  p3d_FragColor.rgb = mix(fog_color, p3d_FragColor.rgb, clamp(exp2(0.25 * (-vpos.z - 10) * -1.442695f), 0, 1));

  p3d_FragColor.a = texcol.a * p3d_ColorScale.a;
}
