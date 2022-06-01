//Add item x1 to the shopping cart
function AddItem(UserID, BranchName, MediID, MediBrand, MediName){
    fetch(AddItemURL,{
        method: 'POST',
        body: JSON.stringify({
            UserID: UserID,
            MediID: MediID,
            BranchName: BranchName
        }),
        headers: {
            "X-CSRFToken" : CSRFToken,
            'Content-type': 'application/json; charset=UTF-8'
        }
    })
    .then(Resp => Resp.text())
    .then(function(Data){
        if (parseInt(Data)){
            alert("成功向购物车添加药品 " + MediName + "(" + MediID + " " + MediBrand + ")一份，院区：" + BranchName + ".");
        }else{
            alert("药品添加失败 " + MediName + "(" + MediID + " " + MediBrand + ")，院区：" + BranchName + "。请刷新页面");
            location.reload();
        }
    });
}

//Commit the current bill
function Checkout(UserID, BranchName){
    fetch(CommitBillURL,{
        method: 'POST',
        body: JSON.stringify({
            UserID: UserID,
            BranchName: BranchName
        }),
        headers: {
            "X-CSRFToken" : CSRFToken,
            'Content-type': 'application/json; charset=UTF-8'
        }
    })
    .then(Resp => Resp.text())
    .then(function(Data){
        if (parseInt(Data)){
            //Redirect
            location = CheckOutURL+BranchName+"/";
        }else{
            alert("服务器内部错误");
            //Redirect
            location.reload();
        }
        
    });
}

//Update sum
function UpdateSum(BillID){
    //Get the corresponding element that displays sum
    SumEle = document.getElementById(BillID+"_Sum");
    //Get the element corresponding to this bill
    BillEle = document.getElementById(BillID+"_Products");
    //Get the element corresponding to the checkout button
    CheckoutEle = document.getElementById(BillID+"_Checkout");
    //Calculate
    Sum = 0;
    for(var i = 0; i < BillEle.children.length;){
        Quantity = document.getElementById(BillEle.children[i].id+"_Quantity");
        if (Quantity.value == 0){
            //Remove entry
            BillEle.removeChild(BillEle.children[i]);
            continue;
        }
        Price = document.getElementById(BillEle.children[i].id+"_Price");
        Sum += Quantity.value*Price.innerHTML.substr(1);
        i++;
    }
    SumEle.innerHTML = "总价: ￥"+Sum.toFixed(2);
    //Enable or disable the checkout button
    if (Sum == 0)
        CheckoutEle.setAttribute("disabled", "");
    else
        CheckoutEle.removeAttribute("disabled");
}

//Update the sums of all bills
function UpdateSumAll(){
    BillContainer = document.getElementById("BillContainer");
    for(var i = 0; i < BillContainer.children.length; i++){
        BillID_Bill = BillContainer.children[i].id;
        BillID = BillID_Bill.substring(0, BillID_Bill.indexOf('_'));
        UpdateSum(BillID);
    }
}

function SetItem(BillID, UserID, MediID, BranchName, Num){
    fetch(SetItemURL,{
        method: 'POST',
        body: JSON.stringify({
            UserID: UserID,
            MediID: MediID,
            BranchName: BranchName,
            Num: Num
        }),
        headers: {
            "X-CSRFToken" : CSRFToken,
            'Content-type': 'application/json; charset=UTF-8'
        }
    })
    .then(Resp => Resp.text())
    .then(function(Data){
        if (parseInt(Data)){
            UpdateSum(BillID);
        }else{
            alert("无法修改该药品数量。请刷新界面.");
            location.reload();
        }
    });
}