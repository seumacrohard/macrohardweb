/**
 *
 */

$(function() {
    $('#btnupdate').click(function () {

        var ptype=$("input[name='type']").val();
        var pnumber=$("input[name='number']").val();
        var pprice=$("input[name='price']").val();
        var location=$("input[name='location']").val();
        if(ptype==''||ptype==undefined||ptype==null){
            alert("请输入商品种类");
        }
        else if(pnumber==''||pnumber==undefined||pnumber==null){
            alert("请输入商品库存数量");
        }
        else if( pprice==''||pprice==undefined||pprice==null){
            alert("请输入商品单价");
        }
        else if( location==''||location==undefined||location==null){
            alert("请输入商品货架位置");
        }
        else{
            $('#updatefrm').submit();
            alert("修改成功");
        }
    });
});

$(function() {
    $('#btndelete').click(function () {
        var msg="确定要删除吗？";
        if(confirm(msg)==true){
            $('#deletefrm').submit();
            alert("删除成功");
        }
        else{
            return false;
        }
    });
});

$(function() {
    $('#btnadd').click(function () {
        var formData= new FormData();
        var proID=$("input[name='productId']").val();
        var proName=$("input[name='productName']").val();
        var ptype=$("input[name='type']").val();
        var pnumber=$("input[name='number']").val();
        var pprice=$("input[name='price']").val();
        var pdateofproduce=$("input[name='dateofproduce']").val();
        var pdateofbad=$("input[name='dateofbad']").val();
        var location=$("input[name='location']").val();
        var file=$("#myFile").val();
        if(proID==''||proID=='undefined'||proID==null){
            alert("请输入商品ID");
        }
        else if(proName==''||proName==undefined||proName==null){
            alert("请输入商品名称");
        }
        else if(ptype==''||ptype==undefined||ptype==null){
            alert("请输入商品种类");
        }
        else if(pnumber==''||pnumber==undefined||pnumber==null){
            alert("请输入商品库存数量");
        }
        else if( pprice==''||pprice==undefined||pprice==null){
            alert("请输入商品单价");
        }
        else if(pdateofproduce==''||pdateofproduce==undefined||pdateofproduce==null){
            alert("请输入商品生产日期");
        }
        else if(pdateofbad==''||pdateofbad==undefined||pdateofbad==null){
            alert("请输入商品保质日期");
        }
        else if(location==''||location==undefined||location==null){
            alert("请输入商品货架位置");
        }
        else if(file==''){
            alert("请添加图片");
        }
        else{
            // formData.append("proID",proID);
            // formData.append("proName",proName);
            // formData.append("ptype",ptype);
            // formData.append("pnumber",pnumber);
            // formData.append("pprice",pprice);
            // formData.append("pdateofproduce",pdateofproduce);
            // formData.append("pdateofbad",pdateofbad);
            // formData.append("file",file);
            alert(file)
            $('#frm').submit();

        }
    });
});

$(function() {
    $('#btnsearch').click(function () {
        var proID=$("input[name='proID']").val();
        if(proID==''||proID=='undefined'||proID==null){
            alert("请输入商品ID");
        }
        else {
            $('#frm').submit();
        }
    });
});






var fileObj = "";
var imgData = "";

$("#myFile").change(function () {
    // 构造一个文件渲染对象
    var reader = new FileReader();
    // 得到文件列表数组
    fileObj = $(this)[0].files[0];
    // 拿到文件数据
    reader.readAsDataURL(fileObj);

    reader.onload = function() {
        // 获取文件信息
        imgData = reader.result;
        // 指定位置显示图片
        $("#myImg").attr("src", imgData);

    };
});


