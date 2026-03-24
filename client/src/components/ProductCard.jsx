import React from 'react';
import PropTypes from 'prop-types';

const ProductCard = ({ product, isAdmin, onEdit, onDelete }) => {
  const finalPrice = product.price - (product.price * product.discount / 100);
  
  let bgColor = '#FFFFFF';
  if (product.quantity === 0) {
    bgColor = 'lightblue';
  } else if (product.discount > 15) {
    bgColor = '#2E8B57';
  }


  const imageSrc = product.icon_link && product.icon_link !== 'picture.png'
    ? `http://127.0.0.1:5000/static/images/${product.icon_link}` 
    : '/picture.png';

  return (
    <div className="product-card" style={{ backgroundColor: bgColor }}>
      <img src={imageSrc} alt={product.name} className="product-image" />
      
      <div className="product-info">
        <h3>{product.category_name} | {product.name}</h3>
        <p><strong>Артикул:</strong> {product.article}</p>
        <p><strong>Описание:</strong> {product.description}</p>
        <p><strong>Производитель:</strong> {product.manufacturer_name}</p>
        
        <div>
          <strong>Цена: </strong>
          {product.discount > 0 ? (
            <>
              <span className="old-price">{product.price.toFixed(2)} руб.</span>
              <span className="new-price">{finalPrice.toFixed(2)} руб.</span>
            </>
          ) : (
            <span className="new-price">{product.price.toFixed(2)} руб.</span>
          )}
        </div>
        <p><strong>На складе:</strong> {product.quantity} шт.</p>

        {isAdmin && (
          <div className="admin-actions">
            <button className="btn-edit" onClick={() => onEdit(product)}>Редактировать</button>
            <button className="btn-delete" onClick={() => onDelete(product.id)}>Удалить</button>
          </div>
        )}
      </div>

      <div className="product-discount-box">
        {product.discount > 0 ? `Скидка ${product.discount}%` : 'Нет скидки'}
      </div>
    </div>
  );
};

ProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    article: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    discount: PropTypes.number.isRequired,
    quantity: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
    icon_link: PropTypes.string,
    category_name: PropTypes.string,
    manufacturer_name: PropTypes.string,
    supplier_name: PropTypes.string,
    category_id: PropTypes.number,
    manufacturer_id: PropTypes.number,
    supplier_id: PropTypes.number,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default ProductCard;