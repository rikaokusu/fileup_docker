particlesJS('particles-js',{
    "particles":{
   
  //--シェイプの設定----------
        "number":{
          "value":40, //シェイプの数
          "density":{
            "enable":true, //シェイプの密集度を変更するか否か
            "value_area":1842 //シェイプの密集度
          }
        },
        "shape":{
          "type":"polygon", //シェイプの形（circle:丸、edge:四角、triangle:三角、polygon:多角形、star:星型、image:画像）
          "stroke":{
            "width":0, //シェイプの外線の太さ
            "color":"#000000" //シェイプの外線の色
          },
          //typeをpolygonにした時の設定
          "polygon": {
            "nb_sides": 6 //多角形の角の数
          },
        },
        "color":{
          "value":"#005392" //シェイプの色
        },
        "opacity":{
          "value":0.2, //シェイプの透明度
          "random":false, //シェイプの透明度をランダムにするか否か
          "anim":{
            "enable":false, //シェイプの透明度をアニメーションさせるか否か
            "speed":1, //アニメーションのスピード
            "opacity_min":0.1, //透明度の最小値
            "sync":false //全てのシェイプを同時にアニメーションさせるか否か
          }
        },
        "size":{
          "value":60, //シェイプの大きさ
          "random":true, //シェイプの大きさをランダムにするか否か
          "anim":{
            "enable":false, //シェイプの大きさをアニメーションさせるか否か
            "speed":40, //アニメーションのスピード
            "size_min":0.1, //大きさの最小値
            "sync":false //全てのシェイプを同時にアニメーションさせるか否か
          }
        },
  //--------------------
  
  //--線の設定----------
        "line_linked":{
          "enable":false, //線を表示するか否か
        },
  //--------------------
  
  //--動きの設定----------
        "move":{
          "enable":true,
          "speed":4.8, //シェイプの動くスピード
          "random":false,
          "straight":false, //個々のシェイプの動きを止めるか否か
          "direction":"none", //エリア全体の動き(none、top、top-right、right、bottom-right、bottom、bottom-left、left、top-leftより選択)
          "out_mode":"bounce", //エリア外に出たシェイプの動き(out、bounceより選択)
          "bounce":false,
          "attract":{"enable":false,"rotateX":600,"rotateY":1200}
        }
  //--------------------
  
      },
   
      "interactivity":{
        "detect_on":"canvas",
        "events":{
  
  //--マウスオーバー時の処理----------
          "onhover":{
            "enable":false, //マウスオーバーが有効か否か
          },
  //--------------------
  
  //--クリック時の処理----------
          "onclick":{
            "enable":false, //クリックが有効か否か
          },
  //--------------------
        "resize":true
        },
   
        "modes":{
    
  //--シェイプが膨らむ----------
          "bubble":{
            "distance":2, //カーソルからの反応距離
            "size":40, //シェイプの膨らむ大きさ
            "opacity":8, //膨らむシェイプの透明度
            "duration":2, //膨らむシェイプの持続時間(onclick時のみ)
            "speed":3 //膨らむシェイプの速度(onclick時のみ)
          },
  //--------------------
  
  //--シェイプが増える----------
          "push":{
            "particles_nb":4 //増えるシェイプの数
          },
  //--------------------
  
        }
      },
      "retina_detect":true, //Retina Displayを対応するか否か
      "resize":true //canvasのサイズ変更にわせて拡大縮小するか否か
    }
  );