const BP = {
  pm25: { C:[0,12.1,35.5,55.5,150.5,250.5,350.5,500.5], I:[0,51,101,151,201,301,401,500] },
  pm10: { C:[0,55,155,255,355,425,505,605],              I:[0,51,101,151,201,301,401,500] },
  no2:  { C:[0,54,101,361,650,1250,1650,2049],           I:[0,51,101,151,201,301,401,500] },
  so2:  { C:[0,36,76,186,305,605,805,1005],              I:[0,51,101,151,201,301,401,500] },
  co:   { C:[0,4.5,9.5,12.5,15.5,30.5,40.5,50.5],       I:[0,51,101,151,201,301,401,500] },
  o3:   { C:[0,55,71,86,106,201,300,500],                I:[0,51,101,151,201,300,400,500] },
};

export function subAqi(key, val) {
  const { C, I } = BP[key];
  for (let i = 0; i < C.length - 1; i++) {
    if (val >= C[i] && val < C[i + 1]) {
      return Math.round(((I[i+1]-I[i])/(C[i+1]-C[i]))*(val-C[i])+I[i]);
    }
  }
  return val >= C[C.length - 1] ? 500 : 0;
}

export function estimateAqi(p) {
  return Math.min(500, Math.max(
    subAqi('pm25', p.pm25 || 0),
    subAqi('pm10', p.pm10 || 0),
    subAqi('no2',  p.no2  || 0),
    subAqi('so2',  p.so2  || 0),
    subAqi('co',   p.co   || 0),
    subAqi('o3',   p.o3   || 0),
  ));
}

export function getCategory(aqi) {
  if (aqi <= 50)
    return {
      label: "Good",
      range: "0 – 50",
      tokenClass: "aqi-good",
      hex: "#6bcf7f",
      textOn: "#0a3d14",
      description: "Air quality is satisfactory and poses little or no risk.",
      advice: "Perfect day to be outdoors. Enjoy the fresh air!",
      emoji: "😊",
    };
  if (aqi <= 100)
    return {
      label: "Moderate",
      range: "51 – 100",
      tokenClass: "aqi-moderate",
      hex: "#ffd700",
      textOn: "#3a2a00",
      description: "Acceptable air quality. Minor concern for very sensitive groups.",
      advice: "Unusually sensitive people should consider limiting prolonged exertion.",
      emoji: "🙂",
    };
  if (aqi <= 150)
    return {
      label: "Unhealthy for Sensitive Groups",
      range: "101 – 150",
      tokenClass: "aqi-sensitive",
      hex: "#ff9933",
      textOn: "#3a1a00",
      description: "Sensitive groups may experience health effects.",
      advice: "Children, elderly and those with respiratory issues should limit outdoor activity.",
      emoji: "😐",
    };
  if (aqi <= 200)
    return {
      label: "Unhealthy",
      range: "151 – 200",
      tokenClass: "aqi-unhealthy",
      hex: "#ff4444",
      textOn: "#ffffff",
      description: "Everyone may begin to experience health effects.",
      advice: "Reduce prolonged outdoor exertion. Consider wearing a mask.",
      emoji: "😷",
    };
  if (aqi <= 300)
    return {
      label: "Very Unhealthy",
      range: "201 – 300",
      tokenClass: "aqi-very-unhealthy",
      hex: "#993399",
      textOn: "#ffffff",
      description: "Health alert: serious effects for everyone.",
      advice: "Avoid outdoor activity. Keep windows closed; use air purifiers.",
      emoji: "🤢",
    };
  return {
    label: "Hazardous",
    range: "301+",
    tokenClass: "aqi-hazardous",
    hex: "#8b0000",
    textOn: "#ffffff",
    description: "Emergency conditions. Entire population affected.",
    advice: "Stay indoors. Wear N95 masks if you must go out.",
    emoji: "☠️",
  };
}